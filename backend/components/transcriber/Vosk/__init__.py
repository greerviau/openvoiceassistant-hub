from vosk import Model, KaldiRecognizer, SetLogLevel
import json
import os
import wget
import zipfile

from backend.config import Configuration

SetLogLevel(0)

class Vosk:
    def __init__(self, model_folder: str):
        self.vosk_model = Model(model_folder)

    def transcribe(self, wave_file, samplerate):
        rec = KaldiRecognizer(self.vosk_model, samplerate)
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

def build_engine(config: Configuration):
    model_path = config.get('components', 'transcriber', 'config', 'model_path')
    if not model_path:
        model_dump = config.get('model_dump')
        model_path = os.path.join(model_dump, 'vosk_model')
        config.setkey('components', 'transcriber', 'config', 'model_path', value=model_path)
        print(f'Loading vosk model: {model_path}')
    if not os.path.exists(model_path):
        print('Vosk model does not exist')
        print('Downloading vosk model')
        os.makedirs(model_path)
        wget.download('https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip')
        with zipfile.ZipFile('vosk-model-en-us-0.22.zip', 'r') as zip_ref:
            zip_ref.extractall(model_path)
        os.remove('vosk-model-en-us-0.22.zip')
            
    return Vosk(model_path)

def default_config():
    return {
        "model_path": ""
    }