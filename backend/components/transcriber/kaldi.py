from vosk import Model, KaldiRecognizer, SetLogLevel
import json
import os
import wget
import zipfile
import wave

from backend.schemas import Context
from backend.enums import Components
from backend import config
from backend.utils.audio import create_wave, load_wave

SetLogLevel(0)

class Kaldi:
    def __init__(self, ova: 'OpenVoiceAssistant'):
        model_lang = config.get(Components.Transcriber.value, 'config', 'model_lang')
        self.vosk_model = Model(lang=model_lang)

    def transcribe(self, context: Context):

        file_path = context['command_audio_file_path']
        wf = wave.open(file_path, 'rb')
        rec = KaldiRecognizer(self.vosk_model, wf.getframerate())
        res = None
        while True:
            data = wf.readframes(4000)
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

def build_engine(ova: 'OpenVoiceAssistant'):
    return Kaldi(ova)

def default_config():
    return {
        "model_lang": "en-us", 
    }