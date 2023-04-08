import pyttsx3
import wave
import os
import time
import typing

from backend.schemas import Context
from backend import config

class Espeak:

    def synthesize(self, context: Context):
        text = context['response']
        file_path = context['response_audio_file_path']

        tts_engine = pyttsx3.init()
        tts_engine.save_to_file(text, file_path)
        tts_engine.runAndWait()

        audio_seg = wave.open(file_path, 'rb')

        audio_data = audio_seg.readframes(audio_seg.getnframes())

        return audio_data, audio_seg.getframerate(), audio_seg.getsampwidth()

def build_engine() -> Espeak:
    return Espeak()

def default_config() -> typing.Dict:
    return {}