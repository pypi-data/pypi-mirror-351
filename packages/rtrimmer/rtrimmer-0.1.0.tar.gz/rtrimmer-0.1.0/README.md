# rtrimmer

Lightweight Python package to trim RTTM diarization files and optionally audio files to a user-specified time range.

## Features
- Trim RTTM files to a specified time range
- Adjust segment durations if they overlap the max duration
- Optionally trim audio files using ffmpeg
- Batch support for folders
- CLI and Python API
- Logging and input validation

## Installation

```bash
pip install rtrimmer
```

## Usage

### CLI

Trim an RTTM file to the first 5 minutes (300 seconds):

```bash
rttm-trim --rttm input.rttm --output-rttm trimmed.rttm --duration 300
```

Trim both RTTM and audio file:

```bash
rttm-trim --rttm input.rttm --audio input.wav --output-rttm trimmed.rttm --output-audio trimmed.wav --duration 300
```

Batch trim all RTTM files in a folder:

```bash
rttm-trim --rttm-folder ./rttms --output-folder ./trimmed_rttms --duration 300
```

Trim starting from a specific time point (e.g., 60 seconds in) for 5 minutes:

```bash
rttm-trim --rttm input.rttm --output-rttm trimmed.rttm --start-time 60 --duration 300
```

### Python API

```python
from rtrimmer import trim_rttm, trim_audio, trim_rttm_folder

# Trim a single RTTM file
trim_rttm("session1.rttm", "session1_trimmed.rttm", max_duration=300)

# Trim starting from 60 seconds in
trim_rttm("session1.rttm", "session1_trimmed.rttm", max_duration=300, min_time=60)

# Trim audio file
trim_audio("session1.wav", "session1_trimmed.wav", duration=300, start_time=0)

# Batch process a folder of RTTM files
results = trim_rttm_folder("./rttms", "./trimmed_rttms", max_duration=300)
print(f"Processed {len(results)} files")
```

## How It Works

### RTTM Trimming Logic

The package handles various edge cases when trimming RTTM files:

1. **Segments fully within the target range**: Kept as is
2. **Segments starting before the target range but extending into it**: Start time adjusted to the beginning of the target range, duration shortened accordingly
3. **Segments extending beyond the target range**: Duration shortened to end at the target range boundary
4. **Segments outside the target range**: Excluded from the output

### Audio Trimming

Audio trimming is performed using ffmpeg, which must be installed and available in your PATH. The package attempts to use the copy codec for faster processing, but falls back to re-encoding if needed.

## Requirements
- Python 3.8+
- ffmpeg (for audio trimming, must be installed and in PATH)

## Example

Suppose you have a diarization RTTM file and a corresponding WAV file for a 1-hour meeting, but you only want the first 5 minutes:

```bash
rttm-trim --rttm meeting.rttm --audio meeting.wav --output-rttm meeting_5min.rttm --output-audio meeting_5min.wav --duration 300
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
