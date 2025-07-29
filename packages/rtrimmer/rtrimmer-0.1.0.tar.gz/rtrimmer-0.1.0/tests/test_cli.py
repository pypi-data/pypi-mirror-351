"""
Test CLI functionality for rtrimmer.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rtrimmer.cli import main


class TestCLI(unittest.TestCase):
    """Test command-line interface functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.TemporaryDirectory()
        self.input_rttm = Path(self.test_dir.name) / "input.rttm"
        self.output_rttm = Path(self.test_dir.name) / "output.rttm"
        
        # Create a test RTTM file
        with open(self.input_rttm, 'w') as f:
            f.write("SPEAKER test 1 0.5 2.0 <NA> <NA> speaker1 <NA> <NA>\n")
            f.write("SPEAKER test 1 3.0 3.0 <NA> <NA> speaker2 <NA> <NA>\n")
            f.write("SPEAKER test 1 7.0 4.0 <NA> <NA> speaker1 <NA> <NA>\n")
            f.write("SPEAKER test 1 12.0 3.0 <NA> <NA> speaker2 <NA> <NA>\n")
        
        # Create a folder for batch testing
        self.input_folder = Path(self.test_dir.name) / "input_folder"
        self.output_folder = Path(self.test_dir.name) / "output_folder"
        self.input_folder.mkdir()
        
        # Create multiple test RTTM files in the folder
        for i in range(3):
            with open(self.input_folder / f"test{i}.rttm", 'w') as f:
                f.write(f"SPEAKER test{i} 1 0.5 2.0 <NA> <NA> speaker1 <NA> <NA>\n")
                f.write(f"SPEAKER test{i} 1 3.0 3.0 <NA> <NA> speaker2 <NA> <NA>\n")
    
    def tearDown(self):
        """Clean up test environment."""
        self.test_dir.cleanup()
    
    @patch('sys.argv', ['rttm-trim', '--rttm', 'input.rttm', '--output-rttm', 'output.rttm', '--duration', '10'])
    def test_cli_args_parsing(self):
        """Test CLI argument parsing."""
        with patch('rtrimmer.cli.trim_rttm') as mock_trim:
            mock_trim.return_value = 3
            exit_code = main()
            self.assertEqual(exit_code, 0)
            mock_trim.assert_called_once()
    
    def test_single_file_processing(self):
        """Test processing a single RTTM file via CLI."""
        args = [
            '--rttm', str(self.input_rttm),
            '--output-rttm', str(self.output_rttm),
            '--duration', '10'
        ]
        
        exit_code = main(args)
        self.assertEqual(exit_code, 0)
        self.assertTrue(self.output_rttm.exists())
        
        # Check file content
        with open(self.output_rttm, 'r') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 3)  # Should have 3 segments (last one excluded)
    
    def test_batch_processing(self):
        """Test batch processing of RTTM files via CLI."""
        args = [
            '--rttm-folder', str(self.input_folder),
            '--output-folder', str(self.output_folder),
            '--duration', '5'
        ]
        
        exit_code = main(args)
        self.assertEqual(exit_code, 0)
        self.assertTrue(self.output_folder.exists())
        
        # Check that output files were created
        output_files = list(self.output_folder.glob('*.rttm'))
        self.assertEqual(len(output_files), 3)
    
    def test_invalid_arguments(self):
        """Test handling of invalid arguments."""
        # Missing required arguments
        args = ['--duration', '10']
        exit_code = main(args)
        self.assertEqual(exit_code, 1)
        
        # Invalid duration
        args = [
            '--rttm', str(self.input_rttm),
            '--output-rttm', str(self.output_rttm),
            '--duration', '-5'
        ]
        exit_code = main(args)
        self.assertEqual(exit_code, 1)
        
        # Invalid start time
        args = [
            '--rttm', str(self.input_rttm),
            '--output-rttm', str(self.output_rttm),
            '--duration', '10',
            '--start-time', '-5'
        ]
        exit_code = main(args)
        self.assertEqual(exit_code, 1)


if __name__ == '__main__':
    unittest.main()
