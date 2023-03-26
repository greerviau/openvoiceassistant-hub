import pyttsx3
import pydub
import os
import time
import typing

from backend import config

class Espeak:
    def __init__(self):
        self.engine = pyttsx3.init()

    def synthesize(self, text: str, file_path: str):
        self.engine.save_to_file(text, file_path)
        self.engine.runAndWait()
        audio_seg = pydub.AudioSegment.from_file(file_path)
        
        return audio_seg.raw_data, audio_seg.frame_rate, audio_seg.sample_width

def build_engine() -> Espeak:
    return Espeak()

def default_config() -> typing.Dict:
    return {}