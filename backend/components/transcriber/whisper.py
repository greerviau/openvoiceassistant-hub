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
    def __init__(self, ova: 'OpenVoiceAssistant'):
        model_size = config.get(Components.Transcriber.value, 'config', 'model_size')
        self.model = whisper.load_model(model_size)

    def transcribe(self, context: Context):

        file_path = context['command_audio_file_path']
        result = self.model.transcribe(file_path)
        return result["text"]

def build_engine(ova: 'OpenVoiceAssistant'):
    return Whisper(ova)

def default_config():
    return {
        "model_size": "tiny.en",
        "model_sizes": ["tiny.en", "tiny", "base.en", "base", "small.en", "small", "medium.en", "medium", "large"]
    }