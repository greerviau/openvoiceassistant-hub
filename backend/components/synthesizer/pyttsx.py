import pyttsx3
import pydub
import os
from backend.config import Configuration

class Pyttsx:
    def __init__(self):
        self.engine = pyttsx3.init()

    def synthesize(self, text: str, file_dump: str = ''):
        self.engine.save_to_file(text, os.path.join(file_dump, 'response.wav'))
        self.engine.runAndWait()
        audio_seg = pydub.AudioSegment.from_file(os.path.join(file_dump, 'response.wav'))
        
        return audio_seg.raw_data, audio_seg.frame_rate, audio_seg.sample_width

def build_engine(config: Configuration):
    return Pyttsx()

def default_config():
    return {}