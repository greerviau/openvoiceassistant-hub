import whisper
import numpy as np

from backend.config import Configuration

class Whisper:
    def __init__(self, model_size: str):
        self.model = whisper.load_model(model_size)

    def transcribe(self, wave_file, samplerate):
        sample_freq = wave_file.getframerate()
        n_samples = wave_file.getnframes()
        n_channels = wave_file.getnchannels()
        signal_wave = wave_file.readframes(n_samples)

        signal_array = np.frombuffer(signal_wave, dtype=np.int16)

        result = self.model.transcribe(signal_array)

        return result["text"]

def build_engine(config: Configuration):
    model_size = config.get('components', 'transcriber', 'config', 'model_size')
            
    return Whisper(model_size)

def default_config():
    return {
        "model_size": "tiny.en"
    }