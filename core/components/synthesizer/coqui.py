from TTS.api import TTS
import typing
import torch

from core.enums import Components
from core import config

class Coqui:

    def __init__(self, ova: 'OpenVoiceAssistant'):
        print("Loading Coqui Synthesizer")
        self.ova = ova
        model_name = config.get(Components.Synthesizer.value, 'config', 'model')
        use_gpu = config.get(Components.Synthesizer.value, 'config', 'use_gpu')
        use_gpu = torch.cuda.is_available() and use_gpu
        config.set(Components.Synthesizer.value, 'config', 'use_gpu', use_gpu)

        device = "cuda" if use_gpu else "cpu"

        self.tts = TTS(model_name=model_name, progress_bar=False, gpu=use_gpu).to(device)

    def synthesize(self, text: str, file_path: str):
        self.tts.tts_to_file(text=text, file_path=file_path)

def build_engine(ova: 'OpenVoiceAssistant') -> Coqui:
    return Coqui(ova)

def default_config() -> typing.Dict:
    return {
        "id": "coqui",
        "model": "tts_models/en/ljspeech/speedy-speech",
        "use_gpu": False,
        "model_options": TTS().list_models().list_models()
    }