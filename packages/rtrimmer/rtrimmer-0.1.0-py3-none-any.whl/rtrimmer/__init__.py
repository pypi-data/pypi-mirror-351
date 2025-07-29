"""
rtrimmer - Lightweight Python package to trim RTTM diarization files and audio files.
"""

from .core import trim_rttm, trim_audio, trim_rttm_folder
from .version import __version__

__all__ = ['trim_rttm', 'trim_audio', 'trim_rttm_folder', '__version__']
