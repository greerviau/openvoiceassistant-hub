from vosk import Model, KaldiRecognizer, SetLogLevel
import json

SetLogLevel(0)

class Vosk:
    def __init__(self, model_folder):
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

def build_engine(config):
    model_folder = config['model_folder']
    return Vosk(model_folder)