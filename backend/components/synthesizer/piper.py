import pyttsx3
import wave
import soundfile
import os
import time
import typing

from piper.download import ensure_voice_exists, find_voice, get_voices
from piper import PiperVoice
from pathlib import Path

from backend.schemas import Context
from backend import config

class Piper:
    def __init__(self):
        model = 'en_US-lessac-medium'
        data_dir = [str(Path.cwd())]
        download_dir = data_dir[0]

        voices_info = get_voices('./')
        #print(voices_info.keys())

        ensure_voice_exists(model, data_dir, download_dir, voices_info)
        model, config = find_voice('en_US-lessac-medium', data_dir)

        self.voice = PiperVoice.load(model, config_path=config, use_cuda=True)

    def synthesize(self, context: Context):
        text = context['response']
        file_path = context['response_audio_file_path']
        if os.path.isfile(file_path):
            os.remove(file_path)

        with wave.open(file_path, "wb") as wav_file:
            self.voice.synthesize(text, wav_file)

        try:
            audio_seg = wave.open(file_path, 'rb')
        except wave.Error:
            data, samplerate = soundfile.read(file_path)
            soundfile.write(file_path, data, samplerate)
            audio_seg = wave.open(file_path, 'rb')

        audio_data = audio_seg.readframes(audio_seg.getnframes())

        return audio_data, audio_seg.getframerate(), audio_seg.getsampwidth()

def build_engine() -> Piper:
    return Piper()

def default_config() -> typing.Dict:
    return {
        "model": "en_US-lessac-medium",
        "use_gpu": False,
        "available_models": get_voices('./')
    }