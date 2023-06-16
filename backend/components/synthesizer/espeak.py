import pyttsx3
import wave
import soundfile
import typing
import os
import time

from backend.schemas import Context
from backend import config

class Espeak:

    def synthesize(self, context: Context):
        text = context['response']
        file_path = context['response_audio_file_path']
        if os.path.isfile(file_path):
            os.remove(file_path)

        tts_engine = pyttsx3.init()
        tts_engine.save_to_file(text, file_path)
        tts_engine.runAndWait()

        while not os.path.isfile(file_path):
            time.sleep(0.1)

        try:
            audio_seg = wave.open(file_path, 'rb')
        except wave.Error:
            data, samplerate = soundfile.read(file_path)
            soundfile.write(file_path, data, samplerate)
            audio_seg = wave.open(file_path, 'rb')

        audio_data = audio_seg.readframes(audio_seg.getnframes())

        return audio_data, audio_seg.getframerate(), audio_seg.getsampwidth()

def build_engine() -> Espeak:
    return Espeak()

def default_config() -> typing.Dict:
    return {}