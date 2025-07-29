"""
Core functionality for trimming RTTM and audio files.
"""

import os
import logging
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

def parse_rttm_line(line: str) -> Tuple:
    """
    Parse a single line from an RTTM file.
    
    Args:
        line: A line from an RTTM file
        
    Returns:
        Tuple containing the parsed components of the RTTM line
    """
    parts = line.strip().split()
    if len(parts) < 10:
        raise ValueError(f"Invalid RTTM line format: {line}")
    
    # RTTM format: SPEAKER file_id channel start_time duration <NA> <NA> speaker_id <NA> <NA>
    return {
        'type': parts[0],
        'file_id': parts[1],
        'channel': int(parts[2]),
        'start_time': float(parts[3]),
        'duration': float(parts[4]),
        'ortho': parts[5],
        'stype': parts[6],
        'speaker_id': parts[7],
        'conf': parts[8],
        'slat': parts[9]
    }

def format_rttm_line(entry: dict) -> str:
    """
    Format a dictionary of RTTM components back into an RTTM line.
    
    Args:
        entry: Dictionary containing RTTM components
        
    Returns:
        Formatted RTTM line
    """
    return f"{entry['type']} {entry['file_id']} {entry['channel']} {entry['start_time']:.2f} {entry['duration']:.2f} {entry['ortho']} {entry['stype']} {entry['speaker_id']} {entry['conf']} {entry['slat']}"

def trim_rttm(input_path: Union[str, Path], 
              output_path: Union[str, Path], 
              max_duration: float,
              min_time: float = 0.0) -> int:
    """
    Trim an RTTM file to a specified duration.
    
    Args:
        input_path: Path to the input RTTM file
        output_path: Path to save the trimmed RTTM file
        max_duration: Maximum duration in seconds to keep
        min_time: Minimum time in seconds to start from (default: 0.0)
        
    Returns:
        Number of segments in the trimmed output file
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input RTTM file not found: {input_path}")
    
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Trimming {input_path} to {max_duration} seconds, saving to {output_path}")
    
    # Read and process the RTTM file
    with open(input_path, 'r') as f:
        lines = f.readlines()
    
    trimmed_segments = []
    segment_count = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        try:
            entry = parse_rttm_line(line)
            
            # Skip segments that end before the min_time
            if entry['start_time'] + entry['duration'] <= min_time:
                continue
                
            # Skip segments that start after the max_duration
            if entry['start_time'] >= min_time + max_duration:
                continue
                
            # Adjust segments that start before min_time but extend beyond it
            if entry['start_time'] < min_time:
                original_duration = entry['duration']
                entry['duration'] = entry['start_time'] + original_duration - min_time
                entry['start_time'] = min_time
                
            # Adjust segments that extend beyond max_duration
            if entry['start_time'] + entry['duration'] > min_time + max_duration:
                entry['duration'] = min_time + max_duration - entry['start_time']
                
            # Adjust start time relative to new timeline if min_time > 0
            if min_time > 0:
                entry['start_time'] -= min_time
                
            # Only include segments with positive duration
            if entry['duration'] > 0:
                trimmed_segments.append(format_rttm_line(entry))
                segment_count += 1
                
        except (ValueError, IndexError) as e:
            logger.warning(f"Skipping invalid line: {line}. Error: {e}")
    
    # Write the trimmed segments to the output file
    with open(output_path, 'w') as f:
        for segment in trimmed_segments:
            f.write(f"{segment}\n")
    
    logger.info(f"Trimmed RTTM file saved with {segment_count} segments")
    return segment_count

def trim_audio(input_path: Union[str, Path], 
               output_path: Union[str, Path], 
               duration: float,
               start_time: float = 0.0) -> bool:
    """
    Trim an audio file to a specified duration using ffmpeg.
    
    Args:
        input_path: Path to the input audio file
        output_path: Path to save the trimmed audio file
        duration: Duration in seconds to keep
        start_time: Start time in seconds (default: 0.0)
        
    Returns:
        True if successful, False otherwise
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input audio file not found: {input_path}")
    
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Trimming audio {input_path} from {start_time}s to {start_time + duration}s, saving to {output_path}")
    
    try:
        # Check if ffmpeg is available
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        
        # Run ffmpeg command to trim the audio
        cmd = [
            'ffmpeg', 
            '-i', str(input_path),
            '-ss', str(start_time),
            '-t', str(duration),
            '-c', 'copy',  # Use copy codec for faster processing
            '-y',  # Overwrite output file if it exists
            str(output_path)
        ]
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode != 0:
            logger.error(f"ffmpeg error: {result.stderr.decode()}")
            # If copy codec fails, try again with re-encoding
            logger.info("Retrying with re-encoding...")
            cmd[8] = 'aac'  # Replace 'copy' with 'aac' for audio
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if result.returncode != 0:
                logger.error(f"ffmpeg error on retry: {result.stderr.decode()}")
                return False
        
        logger.info(f"Audio trimming completed successfully")
        return True
        
    except FileNotFoundError:
        logger.error("ffmpeg not found. Please install ffmpeg and ensure it's in your PATH.")
        return False
    except subprocess.SubprocessError as e:
        logger.error(f"Error running ffmpeg: {e}")
        return False

def trim_rttm_folder(input_folder: Union[str, Path], 
                     output_folder: Union[str, Path], 
                     max_duration: float,
                     min_time: float = 0.0) -> dict:
    """
    Trim all RTTM files in a folder to a specified duration.
    
    Args:
        input_folder: Path to the folder containing RTTM files
        output_folder: Path to save the trimmed RTTM files
        max_duration: Maximum duration in seconds to keep
        min_time: Minimum time in seconds to start from (default: 0.0)
        
    Returns:
        Dictionary with filenames as keys and number of segments as values
    """
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    
    if not input_folder.exists() or not input_folder.is_dir():
        raise NotADirectoryError(f"Input folder not found or not a directory: {input_folder}")
    
    # Create output directory if it doesn't exist
    output_folder.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Processing all RTTM files in {input_folder}")
    
    results = {}
    rttm_files = list(input_folder.glob('*.rttm'))
    
    if not rttm_files:
        logger.warning(f"No RTTM files found in {input_folder}")
        return results
    
    for rttm_file in rttm_files:
        output_file = output_folder / rttm_file.name
        try:
            segment_count = trim_rttm(rttm_file, output_file, max_duration, min_time)
            results[rttm_file.name] = segment_count
        except Exception as e:
            logger.error(f"Error processing {rttm_file}: {e}")
            results[rttm_file.name] = 0
    
    logger.info(f"Processed {len(results)} RTTM files")
    return results
