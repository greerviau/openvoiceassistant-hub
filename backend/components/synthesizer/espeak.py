import pyttsx3
import pydub
import os
import time
import typing

from backend import config

class Espeak:
    def __init__(self):
        self.tts_engine = pyttsx3.init()

    def synthesize(self, text: str, file_path: str):
        self.tts_engine.save_to_file(text, file_path)
        self.tts_engine.runAndWait()
        self.tts_engine.stop()
        time.sleep(0.2)
        audio_seg = pydub.AudioSegment.from_file(file_path)
        
        return audio_seg.raw_data, audio_seg.frame_rate, audio_seg.sample_width

def build_engine() -> Espeak:
    return Espeak()

def default_config() -> typing.Dict:
    return {}