import whisper
import numpy as np
import typing
import wave
import os

from backend.schemas import Context
from backend.enums import Components
from backend import config
from backend.utils.audio import create_numpy_waveform, resample_waveform

class Whisper:
    def __init__(self):  
        model_size = config.get(Components.Transcriber.value, 'config', 'model_size')
        self.model = whisper.load_model(model_size)

    def transcribe(self, context: Context):

        audio_data = context['command_audio_data_bytes']
        sample_rate = context['command_audio_sample_rate']

        waveform = create_numpy_waveform(audio_data)

        if sample_rate != 16000:
            waveform = resample_waveform(waveform, sample_rate, 16000)

        result = self.model.transcribe(waveform)

        return result["text"]

def build_engine():
    return Whisper()

def default_config():
    return {
        "model_size": "tiny.en",
        "model_sizes": ["tiny.en", "tiny", "base.en", "base", "small.en", "small", "medium.en", "medium", "large"]
    }