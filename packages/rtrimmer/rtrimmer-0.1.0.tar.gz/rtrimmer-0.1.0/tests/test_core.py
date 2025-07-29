"""
Unit tests for rtrimmer core functionality.
"""

import os
import tempfile
import unittest
from pathlib import Path

from rtrimmer.core import trim_rttm, parse_rttm_line, format_rttm_line


class TestRTTMParsing(unittest.TestCase):
    """Test RTTM parsing and formatting functions."""
    
    def test_parse_rttm_line(self):
        """Test parsing an RTTM line."""
        line = "SPEAKER file1 1 10.5 2.3 <NA> <NA> speaker1 <NA> <NA>"
        result = parse_rttm_line(line)
        
        self.assertEqual(result['type'], "SPEAKER")
        self.assertEqual(result['file_id'], "file1")
        self.assertEqual(result['channel'], 1)
        self.assertEqual(result['start_time'], 10.5)
        self.assertEqual(result['duration'], 2.3)
        self.assertEqual(result['speaker_id'], "speaker1")
    
    def test_format_rttm_line(self):
        """Test formatting an RTTM entry back to a line."""
        entry = {
            'type': "SPEAKER",
            'file_id': "file1",
            'channel': 1,
            'start_time': 10.5,
            'duration': 2.3,
            'ortho': "<NA>",
            'stype': "<NA>",
            'speaker_id': "speaker1",
            'conf': "<NA>",
            'slat': "<NA>"
        }
        
        result = format_rttm_line(entry)
        expected = "SPEAKER file1 1 10.50 2.30 <NA> <NA> speaker1 <NA> <NA>"
        self.assertEqual(result, expected)
    
    def test_invalid_rttm_line(self):
        """Test handling of invalid RTTM line."""
        line = "SPEAKER file1 1"  # Too few fields
        with self.assertRaises(ValueError):
            parse_rttm_line(line)


class TestRTTMTrimming(unittest.TestCase):
    """Test RTTM trimming functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.TemporaryDirectory()
        self.input_path = Path(self.test_dir.name) / "input.rttm"
        self.output_path = Path(self.test_dir.name) / "output.rttm"
        
        # Create a test RTTM file
        with open(self.input_path, 'w') as f:
            f.write("SPEAKER test 1 0.5 2.0 <NA> <NA> speaker1 <NA> <NA>\n")
            f.write("SPEAKER test 1 3.0 3.0 <NA> <NA> speaker2 <NA> <NA>\n")
            f.write("SPEAKER test 1 7.0 4.0 <NA> <NA> speaker1 <NA> <NA>\n")
            f.write("SPEAKER test 1 12.0 3.0 <NA> <NA> speaker2 <NA> <NA>\n")
    
    def tearDown(self):
        """Clean up test environment."""
        self.test_dir.cleanup()
    
    def test_basic_trimming(self):
        """Test basic RTTM trimming."""
        # Trim to first 10 seconds
        segment_count = trim_rttm(self.input_path, self.output_path, max_duration=10.0)
        
        # Check that the output file exists
        self.assertTrue(self.output_path.exists())
        
        # Check segment count
        self.assertEqual(segment_count, 3)
        
        # Check file content
        with open(self.output_path, 'r') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 3)
        
        # First two segments should be unchanged
        self.assertIn("SPEAKER test 1 0.50 2.00", lines[0])
        self.assertIn("SPEAKER test 1 3.00 3.00", lines[1])
        
        # Third segment should be trimmed
        self.assertIn("SPEAKER test 1 7.00", lines[2])
    
    def test_trim_with_min_time(self):
        """Test RTTM trimming with a minimum start time."""
        # Trim from 3 seconds to 10 seconds
        segment_count = trim_rttm(self.input_path, self.output_path, max_duration=7.0, min_time=3.0)
        
        # Check segment count
        self.assertEqual(segment_count, 2)
        
        # Check file content
        with open(self.output_path, 'r') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 2)
        
        # First segment should start at 0 (relative to new timeline)
        self.assertIn("SPEAKER test 1 0.00 3.00", lines[0])
        
        # Second segment should be adjusted
        self.assertIn("SPEAKER test 1 4.00", lines[1])
    
    def test_trim_overlapping_segments(self):
        """Test trimming segments that overlap the boundaries."""
        # Create a test file with segments that overlap boundaries
        overlap_path = Path(self.test_dir.name) / "overlap.rttm"
        with open(overlap_path, 'w') as f:
            f.write("SPEAKER test 1 -1.0 3.0 <NA> <NA> speaker1 <NA> <NA>\n")  # Starts before 0
            f.write("SPEAKER test 1 4.0 8.0 <NA> <NA> speaker2 <NA> <NA>\n")   # Extends beyond max
        
        # Trim to 0-5 seconds
        segment_count = trim_rttm(overlap_path, self.output_path, max_duration=5.0)
        
        # Check segment count
        self.assertEqual(segment_count, 2)
        
        # Check file content
        with open(self.output_path, 'r') as f:
            lines = f.readlines()
        
        # First segment should be adjusted to start at 0
        self.assertIn("SPEAKER test 1 0.00 2.00", lines[0])
        
        # Second segment should be trimmed to end at 5
        self.assertIn("SPEAKER test 1 4.00 1.00", lines[1])
    
    def test_file_not_found(self):
        """Test handling of non-existent input file."""
        non_existent = Path(self.test_dir.name) / "non_existent.rttm"
        
        with self.assertRaises(FileNotFoundError):
            trim_rttm(non_existent, self.output_path, max_duration=10.0)


if __name__ == '__main__':
    unittest.main()
