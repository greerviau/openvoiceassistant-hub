import pyttsx3
import wave
import soundfile
import os
import time
import typing

from backend.schemas import Context
from backend import config

class Espeak:

    def synthesize(self, context: Context):
        text = context['response']
        file_path = context['response_audio_file_path']
        if os.path.isfile(file_path):
            os.remove(file_path)

        tts_engine = pyttsx3.init()
        tts_engine.save_to_file(text, file_path)
        tts_engine.runAndWait()

        return True



def build_engine() -> Espeak:
    return Espeak()

def default_config() -> typing.Dict:
    return {}