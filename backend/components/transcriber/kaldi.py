from vosk import Model, KaldiRecognizer, SetLogLevel
import json
import os
import wget
import zipfile
import wave

from backend.schemas import Context
from backend import config
from backend.utils.audio import create_wave, load_wave

SetLogLevel(0)

class Kaldi:
    def __init__(self, model_lang: str):
        self.vosk_model = Model(lang=model_lang)

    def transcribe(self, context: Context):

        audio_data = context['command_audio_data_bytes']
        sample_rate = context['command_audio_sample_rate']
        sample_width = context['command_audio_sample_width']
        channels = context['command_audio_channels']
        
        wave_file = create_wave(
            audio_data=audio_data, 
            sample_rate=sample_rate, 
            sample_width=sample_width, 
            channels=channels
        )

        rec = KaldiRecognizer(self.vosk_model, sample_rate)
        res = None
        while True:
            data = wave_file.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = rec.Result()
                break
            else:
                _ = rec.PartialResult()    
        if not res:
            res = rec.FinalResult()

        command = json.loads(res)['text']

        return command

def build_engine():
    model_lang = config.get('components', 'transcriber', 'config', 'model_lang')
            
    return Kaldi(model_lang)

def default_config():
    return {
        "model_lang": "en-us", 
    }