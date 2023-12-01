from TTS.api import TTS
import wave
import soundfile
import typing

from backend.schemas import Context
from backend.enums import Components
from backend import config

class Coqui:

    def __init__(self, model_name: str, gpu: bool):
        self.tts = TTS(model_name=model_name, progress_bar=False, gpu=gpu)

    def synthesize(self, context: Context):
        text = context['response']
        file_path = context['response_audio_file_path']

        self.tts.tts_to_file(text=text, file_path=file_path)

        try:
            audio_seg = wave.open(file_path, 'rb')
        except wave.Error:
            data, samplerate = soundfile.read(file_path)
            soundfile.write(file_path, data, samplerate)
            audio_seg = wave.open(file_path, 'rb')

        audio_data = audio_seg.readframes(audio_seg.getnframes())

        return audio_data, audio_seg.getframerate(), audio_seg.getsampwidth()

def build_engine() -> Coqui:
    model_name = config.get(Components.Synthesizer.value, 'config', 'model_name')
    gpu = config.get(Components.Synthesizer.value, 'config', 'use_gpu')
    return Coqui(model_name, gpu)

def default_config() -> typing.Dict:
    return {
        "model_name": "tts_models/en/ljspeech/speedy-speech",
        "use_gpu": False,
        "model_names": TTS().list_models()
    }