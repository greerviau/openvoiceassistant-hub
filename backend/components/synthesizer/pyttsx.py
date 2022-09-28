import pyttsx3
import pydub

class Pyttsx:
    def __init__(self):
        self.engine = pyttsx3.init()

    def synthesize(self, text):
        self.engine.save_to_file(text, 'response.wav')
        audio_seg = pydub.AudioSegment.from_file('response.wav')
        
        return audio_seg.raw_data(), audio_seg.frame_rate, audio_seg.sample_width

def build_engine(config):
    return Pyttsx()

def default_config():
    return {}