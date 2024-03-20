import typing
import logging
logger = logging.getLogger("components.understander.rapid_fuzz")

from rapidfuzz import fuzz

from core.enums import Components
from core.schemas import Context
from core import config

class Rapidfuzz:

    def __init__(self, algo_config: typing.Dict, intents: typing.Dict, ova: "OpenVoiceAssistant"):
        logger.info("Loading Rapid Fuzz Classifier")
        self.ova = ova
        self.intents = intents
        self.ratio = algo_config["ratio"]
        self.ratio_options = algo_config["ratio_options"]
        assert self.ratio in self.ratio_options

    def understand(self, context: Context):
        encoded_command = context["encoded_command"]

        conf = 0
        intent = None
        for label, patterns in self.intents.items():
            for pattern in patterns:
                r = getattr(fuzz, self.ratio)(encoded_command, pattern)
                if r > conf:
                    conf = r
                    intent = label
        
        skill, action = intent.split("-")
    
        return skill, action, conf

def build_engine(algo_config: typing.Dict, intents: typing.Dict, ova: "OpenVoiceAssistant") -> Rapidfuzz:
    return Rapidfuzz(algo_config, intents, ova)

def default_config() -> typing.Dict:
    return {
        "id": "rapid_fuzz",
        "ratio": "ratio",
        "ratio_options": [
            "ratio",
            "partial_ratio",
            "token_sort_ratio",
            "token_set_ratio",
            "weighted_ratio",
            "quick_ratio"
        ]
    }