from TTS.api import TTS
import wave
import soundfile
import typing

from backend.schemas import Context
from backend.enums import Components
from backend import config

class Coqui:

    def __init__(self, ova: 'OpenVoiceAssistant'):
        self.ova = ova
        model_name = config.get(Components.Synthesizer.value, 'config', 'model')
        gpu = config.get(Components.Synthesizer.value, 'config', 'use_gpu')

        self.tts = TTS(model_name=model_name, progress_bar=False, gpu=gpu)

    def synthesize(self, context: Context):
        text = context['response']
        file_path = context['response_audio_file_path']

        self.tts.tts_to_file(text=text, file_path=file_path)

        return True

def build_engine(ova: 'OpenVoiceAssistant') -> Coqui:
    return Coqui(ova)

def default_config() -> typing.Dict:
    return {
        "model": "tts_models/en/ljspeech/speedy-speech",
        "use_gpu": False,
        "available_models": TTS().list_models()
    }