"""
Setup script for rtrimmer package.
"""

from setuptools import setup, find_packages

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rtrimmer",
    version="0.1.0",
    author="eddiegulay",
    author_email="edgargulay@outlook.com.com",
    description="Lightweight Python package to trim RTTM diarization files and audio files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eddiegulay/rtrimmer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "rttm-trim=rtrimmer.cli:main",
        ],
    },
    install_requires=[
        "ffmpeg-python>=0.2.0",
        "pyannote.core>=4.5.1"
    ],
    keywords="rttm, diarization, audio, trimming, pyannote",
)
