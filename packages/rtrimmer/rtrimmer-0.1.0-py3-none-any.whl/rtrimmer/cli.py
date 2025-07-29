"""
Command-line interface for rtrimmer.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from .core import trim_rttm, trim_audio, trim_rttm_folder
from .version import __version__

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def setup_parser() -> argparse.ArgumentParser:
    """
    Set up the command-line argument parser.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Trim RTTM diarization files and optionally audio files to a specified time range.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Version information
    parser.add_argument('--version', action='version', version=f'rtrimmer {__version__}')
    
    # Input options - single file mode
    parser.add_argument('--rttm', type=str, help='Path to input RTTM file')
    parser.add_argument('--audio', type=str, help='Path to input audio file (optional)')
    
    # Input options - batch mode
    parser.add_argument('--rttm-folder', type=str, help='Path to folder containing RTTM files for batch processing')
    parser.add_argument('--audio-folder', type=str, help='Path to folder containing audio files for batch processing (optional)')
    
    # Output options
    parser.add_argument('--output-rttm', type=str, help='Path to save trimmed RTTM file')
    parser.add_argument('--output-audio', type=str, help='Path to save trimmed audio file (optional)')
    parser.add_argument('--output-folder', type=str, help='Path to folder for saving trimmed files in batch mode')
    
    # Trimming parameters
    parser.add_argument('--duration', type=float, required=True, help='Duration in seconds to keep')
    parser.add_argument('--start-time', type=float, default=0.0, help='Start time in seconds (default: 0.0)')
    
    # Logging options
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--quiet', action='store_true', help='Suppress all output except errors')
    
    return parser

def validate_args(args: argparse.Namespace) -> bool:
    """
    Validate command-line arguments.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        True if arguments are valid, False otherwise
    """
    # Check for valid input mode
    if not ((args.rttm and args.output_rttm) or 
            (args.rttm_folder and args.output_folder)):
        logger.error("Either --rttm and --output-rttm OR --rttm-folder and --output-folder must be specified")
        return False
    
    # Check for valid duration
    if args.duration <= 0:
        logger.error("Duration must be greater than 0")
        return False
    
    # Check for valid start time
    if args.start_time < 0:
        logger.error("Start time must be non-negative")
        return False
    
    # Check for audio file consistency
    if args.audio and not args.output_audio:
        logger.error("--output-audio must be specified when --audio is provided")
        return False
    
    # Check for audio folder consistency
    if args.audio_folder and not args.output_folder:
        logger.error("--output-folder must be specified when --audio-folder is provided")
        return False
    
    return True

def process_single_file(args: argparse.Namespace) -> bool:
    """
    Process a single RTTM file and optionally an audio file.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        True if processing was successful, False otherwise
    """
    try:
        # Trim RTTM file
        segment_count = trim_rttm(
            args.rttm, 
            args.output_rttm, 
            args.duration, 
            args.start_time
        )
        logger.info(f"Trimmed RTTM file saved with {segment_count} segments")
        
        # Trim audio file if specified
        if args.audio and args.output_audio:
            success = trim_audio(
                args.audio, 
                args.output_audio, 
                args.duration, 
                args.start_time
            )
            if not success:
                logger.error("Failed to trim audio file")
                return False
            logger.info(f"Trimmed audio file saved to {args.output_audio}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return False

def process_batch(args: argparse.Namespace) -> bool:
    """
    Process a folder of RTTM files and optionally audio files.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        True if processing was successful, False otherwise
    """
    try:
        # Trim RTTM files
        results = trim_rttm_folder(
            args.rttm_folder, 
            args.output_folder, 
            args.duration, 
            args.start_time
        )
        
        if not results:
            logger.warning("No RTTM files were processed")
            return False
        
        logger.info(f"Processed {len(results)} RTTM files")
        
        # Trim audio files if specified
        if args.audio_folder:
            audio_folder = Path(args.audio_folder)
            output_folder = Path(args.output_folder)
            
            if not audio_folder.exists() or not audio_folder.is_dir():
                logger.error(f"Audio folder not found or not a directory: {audio_folder}")
                return False
            
            # Process each audio file that corresponds to an RTTM file
            audio_count = 0
            for rttm_file in results.keys():
                # Try common audio extensions
                base_name = Path(rttm_file).stem
                audio_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
                
                for ext in audio_extensions:
                    audio_file = audio_folder / f"{base_name}{ext}"
                    if audio_file.exists():
                        output_audio = output_folder / f"{base_name}{ext}"
                        success = trim_audio(
                            audio_file, 
                            output_audio, 
                            args.duration, 
                            args.start_time
                        )
                        if success:
                            audio_count += 1
                        break
            
            logger.info(f"Processed {audio_count} audio files")
        
        return True
    
    except Exception as e:
        logger.error(f"Error processing batch: {e}")
        return False

def main(args: Optional[list] = None) -> int:
    """
    Main entry point for the command-line interface.
    
    Args:
        args: Command-line arguments (if None, sys.argv is used)
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = setup_parser()
    parsed_args = parser.parse_args(args)
    
    # Configure logging based on verbosity
    if parsed_args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif parsed_args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    # Validate arguments
    if not validate_args(parsed_args):
        return 1
    
    # Process files
    if parsed_args.rttm and parsed_args.output_rttm:
        success = process_single_file(parsed_args)
    else:
        success = process_batch(parsed_args)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
