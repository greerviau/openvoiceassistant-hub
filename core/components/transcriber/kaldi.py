import json
import logging
import typing
import wave

logger = logging.getLogger("components.transcriber.kaldi")

from vosk import KaldiRecognizer, Model, SetLogLevel

from core.schemas import Context

SetLogLevel(-1)


class Kaldi:
    def __init__(self, algo_config: typing.Dict, ova: "OpenVoiceAssistant"):  # noqa: F821
        logger.info("Loading Kaldi Transcriber")
        self.ova = ova
        model_lang = algo_config["model_lang"]
        self.vosk_model = Model(lang=model_lang)

    def transcribe(self, context: Context):
        file_path = context["command_audio_file_path"]
        wf = wave.open(file_path, "rb")
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

        command = json.loads(res)["text"]

        return command


def build_engine(algo_config: typing.Dict, ova: "OpenVoiceAssistant"):  # noqa: F821
    return Kaldi(algo_config, ova)


def default_config():
    return {
        "id": "kaldi",
        "model_lang": "en-us",
    }
