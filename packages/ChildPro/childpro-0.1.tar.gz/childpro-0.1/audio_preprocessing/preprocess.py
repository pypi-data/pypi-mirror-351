# audio_processing/preprocess.py

import os
import tempfile
import logging
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

# Set up logging
from .utils import setup_logging

# Initialize logger
L = logging.getLogger(__name__)
setup_logging()

def preprocess_audio(input_path):
    """
    Enhanced audio preprocessing for low-volume speech.

    This function reads the input audio file, applies various audio enhancements,
    and saves the processed file as a temporary file in MP3 format.

    Parameters:
    - input_path (str): Path to the input audio file.

    Returns:
    - str: Path to the processed temporary file or input file if processing failed.
    """
    try:
        L.info(f"Optimizing audio for ASR: {input_path}")
        
        # Read the audio file
        audio = AudioSegment.from_file(input_path)

        # Convert to mono (single channel)
        audio = audio.set_channels(1)
        
        # Set frame rate (sampling rate) to 16kHz, which is common for ASR tasks
        audio = audio.set_frame_rate(16000)

        # Apply dynamic range compression to normalize the loudest and softest parts
        audio = audio.compress_dynamic_range(
            threshold=-40,  # Lower threshold for compression
            ratio=3,         # Compression ratio
            attack=5,        # Time (in ms) to reach full compression
            release=100      # Time (in ms) to return to normal
        )

        # Apply low-pass filter to remove high frequencies above 4 kHz
        audio = audio.low_pass_filter(4000)

        # Normalize audio to maintain headroom
        audio = audio.normalize(headroom=2)

        # Apply another level of dynamic range compression to make speech clearer
        audio = audio.compress_dynamic_range(
            threshold=-55,
            ratio=6,
            attack=15,
            release=200
        )

        # Enhance low-volume speech by applying high-pass filter (for rumbling noises)
        audio = audio.high_pass_filter(80)

        # Boost frequencies around 1000Hz for better clarity in speech
        boosted = audio.high_pass_filter(1000).apply_gain(+4)

        # Overlay the boosted audio to enhance speech clarity in the original
        audio = audio.overlay(boosted)

        # Output to a temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix=".mp3")
        os.close(temp_fd)

        # Export the processed audio to the temporary file
        audio.export(
            temp_path,
            format="mp3",
            codec="libmp3lame",
            bitrate="96k",
            tags={"title": "BA_Optimized"},
            parameters=[
                "-compression_level", "2",
                "-reservoir", "0",
                "-joint_stereo", "0"
            ]
        )

        return temp_path

    except CouldntDecodeError:
        L.error(f"Audio decoding failed: {input_path}")
        return input_path
    except Exception as e:
        L.error(f"Audio processing error: {str(e)}")
        return input_path
