import pyttsx3
import pydub
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

        audio_seg = pydub.AudioSegment.from_file(file_path)

        audio_data = audio_seg.raw_data

        return audio_data, audio_seg.frame_rate, audio_seg.sample_width

def build_engine() -> Espeak:
    return Espeak()

def default_config() -> typing.Dict:
    return {}