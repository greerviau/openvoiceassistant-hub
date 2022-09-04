from vosk import Model, KaldiRecognizer, SetLogLevel
import json

SetLogLevel(0)

class SpeechRecog:
    def __init__(self, model_name):
        self.vosk_model = Model(model_name)

    def recog_audio(self, wave_file, samplerate):
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
