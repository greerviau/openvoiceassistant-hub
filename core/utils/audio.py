import wave
import os
import numpy as np
import librosa
import io
import logging
logger = logging.getLogger("utils.audio")

def save_wave(wave_file: str, audio_data: bytes, sample_rate: int, sample_width: int, channels: int):

    wf = wave.open(wave_file, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sample_width)
    wf.setframerate(sample_rate)
    wf.writeframes(audio_data)

def create_wave(audio_data: bytes, sample_rate: int, sample_width: int, channels: int) -> wave.Wave_read:
    
    wav_data = convert_to_wav(audio_data, sample_rate, sample_width, channels)
    wf = wave.open(io.BytesIO(wav_data), 'rb')

    return wf

def convert_to_wav(audio_data: bytes, sample_rate: int, sample_width: int, channels: int) -> bytes:
    wave_io = io.BytesIO()
    wf = wave.open(wave_io, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sample_width)
    wf.setframerate(sample_rate)
    wf.writeframes(audio_data)

    return wave_io.getvalue()

def load_wave(wave_file_path: str):
    if not os.path.exists(wave_file_path):
        raise RuntimeError('Audio file does not exist')
    return wave.open(wave_file_path, 'rb')

def create_numpy_waveform(audio_data: bytes):
    return np.frombuffer(audio_data, dtype=np.int16).flatten().astype(np.float32) / 32768.0

def resample_waveform(y: np.ndarray, sr_native: int, sr_resample: int) -> np.ndarray:
    logger.info('Re-sampling waveform')
    return librosa.resample(y, orig_sr=sr_native, target_sr=sr_resample)