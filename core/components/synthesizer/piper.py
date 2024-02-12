import wave
import os
import typing
import torch

from piper.download import ensure_voice_exists, find_voice, get_voices
from piper import PiperVoice

from core.enums import Components
from core import config

class Piper:
    def __init__(self, ova: 'OpenVoiceAssistant'):
        print("Loading Piper Synthesizer")
        self.ova = ova
        file_dump = ova.model_dump
        model_name = config.get(Components.Synthesizer.value, 'config', 'model')
        use_gpu = config.get(Components.Synthesizer.value, 'config', 'use_gpu')
        use_gpu = torch.cuda.is_available() and use_gpu
        config.set(Components.Synthesizer.value, 'config', 'use_gpu', use_gpu)

        data_dir = [file_dump]
        download_dir = data_dir[0]

        voices_info = get_voices(download_dir)
        #print(voices_info.keys())

        ensure_voice_exists(model_name, data_dir, download_dir, voices_info)
        model, model_config = find_voice(model_name, data_dir)

        self.voice = PiperVoice.load(model, config_path=model_config, use_cuda=use_gpu)

    def synthesize(self, text: str, file_path: str):
        if os.path.isfile(file_path):
            os.remove(file_path)

        with wave.open(file_path, "wb") as wav_file:
            self.voice.synthesize(text, wav_file)

def build_engine(ova: 'OpenVoiceAssistant') -> Piper:
    return Piper(ova)

def default_config() -> typing.Dict:
    return {
        "id": "piper",
        "model": "en_US-lessac-medium",
        "use_gpu": False,
        "model_options": list(get_voices('./').keys())
    }