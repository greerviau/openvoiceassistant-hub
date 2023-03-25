import whisper
import numpy as np
import typing
import wave
import os

from backend import config
from backend.utils.audio import create_numpy_waveform, resample_waveform

class Whisper:
    def __init__(self, model_size: str):
        self.model = whisper.load_model(model_size)

    def transcribe(self, audio_data: bytes, samplerate: int, samplewidth: int, channels: int, file_path: str):

        waveform = create_numpy_waveform(audio_data)

        if samplerate != 16000:
            waveform = resample_waveform(waveform, samplerate, 16000)

        result = self.model.transcribe(waveform)

        return result["text"]

def build_engine():
    model_size = config.get('components', 'transcriber', 'config', 'model_size')
            
    return Whisper(model_size)

def default_config():
    return {
        "model_size": "tiny.en",
        "model_sizes": ["tiny.en", "tiny", "base.en", "base", "small.en", "small", "medium.en", "medium", "large"]
    }