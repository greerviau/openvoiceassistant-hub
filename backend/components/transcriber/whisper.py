import torch
from faster_whisper import WhisperModel

from backend.schemas import Context
from backend.enums import Components
from backend import config

class Whisper:
    def __init__(self, ova: 'OpenVoiceAssistant'):
        self.ova = ova
        model_size = config.get(Components.Transcriber.value, 'config', 'model_size')
        gpu = config.get(Components.Transcriber.value, 'config', 'use_gpu')

        use_gpu = torch.cuda.is_available() and gpu

        device = "cuda" if torch.cuda.is_available() and gpu else "cpu"

        self.model = WhisperModel(model_size, device=device, compute_type="int8_float16" if use_gpu else "int8")

    def transcribe(self, context: Context):

        file_path = context['command_audio_file_path']
        segments, _ = self.model.transcribe(file_path)
        segments = list(segments)
        #print(segments)
        return " ".join([segment.text for segment in segments])

def build_engine(ova: 'OpenVoiceAssistant'):
    return Whisper(ova)

def default_config():
    return {
        "whisper": True,
        "model_size": "tiny.en",
        "model_sizes": ["tiny.en", "tiny", "base.en", "base", "small.en", "small", "medium.en", "medium", "large"],
        "use_gpu": False
    }