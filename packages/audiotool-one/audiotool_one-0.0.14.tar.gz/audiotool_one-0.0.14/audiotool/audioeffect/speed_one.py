try:
    from audiostretchy.stretch import AudioStretch
except ImportError as e:
    pass
import os
import soundfile as sf
import numpy as np
from loguru import logger
from pydub import AudioSegment


def _stretch_audio(
    input_path: str,
    output_path: str,
    ratio: float = 1.0,
    gap_ratio: float = 0.0,
    upper_freq: int = 333,
    lower_freq: int = 55,
    buffer_ms: float = 25,
    threshold_gap_db: float = -40,
    double_range: bool = False,
    fast_detection: bool = False,
    normal_detection: bool = False,
    sample_rate: int = 0,
):

    audio_stretch = AudioStretch()
    audio_stretch.open(input_path)
    audio_stretch.stretch(
        ratio,
        gap_ratio,
        upper_freq,
        lower_freq,
        buffer_ms,
        threshold_gap_db,
        double_range,
        fast_detection,
        normal_detection,
    )
    audio_stretch.resample(sample_rate)
    audio_stretch.samples = audio_stretch.samples[: int(audio_stretch.nframes * ratio)]
    audio_stretch.save(output_path)


def stretch_speech_friendly(input_path, ratio=0.9, output_path=None):
    """
    ratio = 0.9: slower down into 90% duration
    ratio = 1.2: speed up into 120% duration
    """
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + "_stretch.wav"

    # check if input path is int16 saved, if not changed into, override original one
    data, sr = sf.read(input_path)

    # If the audio is not in int16 format, convert it
    if data.dtype != np.int16:
        logger.warning(f"Converting {input_path} to int16 format...")
        data = np.int16(data * 32767)  # Scale float32 to int16 range
        sf.write(input_path, data, sr, subtype="PCM_16")

    # Perform time-stretching
    try:
        output_path = _stretch_audio(input_path, output_path, ratio=ratio)
    except Exception as e:
        logger.error(f"Error in _stretch_audio: {e}")
        logger.info(
            "make sure audiostretchy installed, or using stretch_speech_pydub function instead."
        )

    # print(f"Stretched audio saved to {output_path}")
    return output_path


def stretch_speech_pydub(input_path, ratio=0.9, output_path=None):
    """
    Stretch or compress speech duration using pydub.

    ratio < 1.0: Slow down audio (e.g., ratio=0.9 slows down to 90% duration).
    ratio > 1.0: Speed up audio (e.g., ratio=1.2 speeds up to 120% duration).
    """
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + "_stretch.wav"

    # Load the audio
    audio = AudioSegment.from_file(input_path)

    # Ensure audio is in int16 format
    if audio.sample_width != 2:  # sample_width of 2 bytes corresponds to int16
        print(f"Converting {input_path} to int16 format...")
        audio = audio.set_sample_width(2)

    # Adjust speed using pydub's speedup feature
    if ratio < 1.0:
        # Slowing down is not directly supported by pydub; adjust via inverse ratio
        speedup_ratio = 1 / ratio
        audio = audio.speedup(playback_speed=speedup_ratio)
    else:
        # Speed up directly
        audio = audio.speedup(playback_speed=ratio)

    # Export the adjusted audio
    audio.export(output_path, format="wav")
    # print(f"Stretched audio saved to {output_path}")
    return output_path
