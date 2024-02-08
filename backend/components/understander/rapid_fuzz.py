import os
import json

import typing
from rapidfuzz import fuzz

from backend.enums import Components
from backend.schemas import Context
from backend import config

class Rapidfuzz:

    def __init__(self, ova: 'OpenVoiceAssistant', intents: typing.Dict):
        print("Loading Rapid Fuzz Classifier")
        self.ova = ova
        self.intents = intents
        self.conf_thresh = config.get(Components.Understander.value, 'config', 'conf_thresh')
        self.ratio = config.get(Components.Understander.value, 'config', 'ratio')
        self.ratio_options = config.get(Components.Understander.value, 'config', 'ratio_options')
        assert self.ratio in self.ratio_options

    def understand(self, context: Context):
        encoded_command = context['encoded_command']

        conf = 0
        intent = None
        for label, patterns in self.intents.items():
            for pattern in patterns:
                r = getattr(fuzz, self.ratio)(encoded_command, pattern)
                if r > conf:
                    conf = r
                    intent = label
        
        skill, action = intent.split('-')

        pass_threshold = True
        if conf < self.conf_thresh:
            pass_threshold = False
    
        return skill, action, conf, pass_threshold

def build_engine(ova: 'OpenVoiceAssistant', intents: typing.Dict) -> Rapidfuzz:
    return Rapidfuzz(ova, intents)

def default_config() -> typing.Dict:
    return {
        "id": "rapid_fuzz",
        "conf_thresh": 80,
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