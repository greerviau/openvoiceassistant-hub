import wave
import numpy as np
import librosa
from io import BytesIO

def save_wave(wave_file: str, audio_data: bytes, sample_rate: int, sample_width: int, channels: int):

    wf = wave.open(wave_file, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sample_width)
    wf.setframerate(sample_rate)
    wf.writeframes(audio_data)

def create_wave(audio_data: bytes, sample_rate: int, sample_width: int, channels: int) -> wave.Wave_read:
    
    wf = wave.open(BytesIO, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sample_width)
    wf.setframerate(sample_rate)
    wf.writeframes(audio_data)

    return wf

def create_numpy_waveform(audio_data: bytes):
    return np.frombuffer(audio_data, dtype=np.int16).flatten().astype(np.float32) / 32768.0

def resample_waveform(y: np.ndarray, sr_native: int, sr_resample: int) -> np.ndarray:
    return librosa.resample(y, orig_sr=sr_native, target_sr=sr_resample)