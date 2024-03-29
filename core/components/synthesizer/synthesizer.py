import importlib
import os
import typing
import time
import uuid
import logging
logger = logging.getLogger("components.synthesizer")

from core import config
from core.dir import FILESDIR
from core.enums import Components
from core.schemas import Context

class Synthesizer:
    def __init__(self, ova: "OpenVoiceAssistant"):
        self.ova = ova

        self.algo = config.get(Components.Synthesizer.value, "algorithm").lower().replace(" ", "_")
        self.module = importlib.import_module(f"core.components.synthesizer.{self.algo}")

        self.verify_algo_config()

        algo_config = config.get(Components.Synthesizer.value, "config")

        self.engine = self.module.build_engine(algo_config, ova)

    def verify_algo_config(self):
        current_config = config.get(Components.Synthesizer.value, "config")
        default_config = self.module.default_config()
        try:
            if not current_config or (current_config.keys() != default_config.keys()) or current_config["id"] != default_config["id"]:
                raise Exception("Incorrect config")
        except:
            config.set(Components.Synthesizer.value, "config", default_config)

    def get_algorithm_default_config(self, algorithm_id: str) -> typing.Dict:
        try:
            module = importlib.import_module(f"core.components.synthesizer.{algorithm_id}")
            return module.default_config()
        except Exception as e:
            raise RuntimeError("Synthesizer algorithm does not exist")
    
    def run_stage(self, context: Context):
        logger.info("Synthesizer Stage")
        start = time.time()
        
        _id = context["node_id"] if "node_id" in context else ""
        if not _id:
            _id = uuid.uuid4().hex
        
        response_file_path = os.path.join(FILESDIR, f"response_{_id}.wav")
        context["response_audio_file_path"] = response_file_path

        response = context["synth_response"]
        logger.info(f"Response: {response}")
        if response:
            try:
                self.engine.synthesize(response, response_file_path)
            except Exception as e:
                raise RuntimeError(f"Failed to synthesize | {repr(e)}")

            context["response_audio_data"] = open(response_file_path, "rb").read().hex()

        else:
            context["response_audio_data"] = ""
            
        dt = time.time() - start
        logger.info(f"Time to synthesize: {dt}")
        context["time_to_synthesize"] = dt
