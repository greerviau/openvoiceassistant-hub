import pyttsx3
import pydub
import os
import time
import typing

from backend.schemas import Context
from backend import config

class Espeak:
    def __init__(self):
        self.tts_engine = pyttsx3.init()

    def synthesize(self, context: Context):
        text = context['response']
        file_path = context['response_audio_file_path']

        self.tts_engine.save_to_file(text, file_path)
        self.tts_engine.runAndWait()
        self.tts_engine.stop()
        time.sleep(0.2)
        
        audio_seg = pydub.AudioSegment.from_file(file_path)

        audio_data = audio_seg.raw_data

        context['response_audio_data_str'] = audio_data.hex()
        context['response_audio_sample_rate'] = audio_seg.frame_rate
        context['response_audio_sample_width'] = audio_seg.sample_width

def build_engine() -> Espeak:
    return Espeak()

def default_config() -> typing.Dict:
    return {}