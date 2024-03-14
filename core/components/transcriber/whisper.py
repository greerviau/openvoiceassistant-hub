import torch
import typing
import logging
logger = logging.getLogger("components.understander.whisper")

from faster_whisper import WhisperModel

from core.schemas import Context
from core.enums import Components
from core import config

class Whisper:
    def __init__(self, algo_config: typing.Dict, ova: "OpenVoiceAssistant"):
        logger.info("Loading Whisper Transcriber")
        self.ova = ova
        model_size = algo_config["model_size"]
        use_gpu = algo_config["use_gpu"]
        use_gpu = torch.cuda.is_available() and use_gpu
        config.set(Components.Transcriber.value, "config", "use_gpu", use_gpu)

        device = "cuda" if use_gpu else "cpu"

        self.model = WhisperModel(model_size, device=device, compute_type="float32" if use_gpu else "int8")

    def transcribe(self, context: Context):

        file_path = context["command_audio_file_path"]
        segments, _ = self.model.transcribe(file_path, beam_size=5)
        segments = list(segments)
        return " ".join([segment.text for segment in segments])

def build_engine(algo_config: typing.Dict, ova: "OpenVoiceAssistant"):
    return Whisper(algo_config, ova)

def default_config():
    return {
        "id": "whisper",
        "model_size": "tiny.en",
        "model_size_options": ["tiny.en", "tiny", "base.en", "base", "small.en", "small", "medium.en", "medium", "large"],
        "use_gpu": False
    }