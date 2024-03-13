import pyttsx3
import os
import time
import typing
import logging
logger = logging.getLogger("components.synthesizer.espeak")

class Espeak:

    def __init__(self, ova: "OpenVoiceAssistant"):
        logger.info("Loading Espeak Synthesizer")
        self.ova = ova

    def synthesize(self, text: str, file_path: str):
        if os.path.isfile(file_path):
            os.remove(file_path)

        tts_engine = pyttsx3.init()
        tts_engine.save_to_file(text, file_path)
        tts_engine.runAndWait()
        while not os.path.exists(file_path):
            time.sleep(0.1)

def build_engine(ova: "OpenVoiceAssistant") -> Espeak:
    return Espeak(ova)

def default_config() -> typing.Dict:
    return {
        "id": "espeak"
    }