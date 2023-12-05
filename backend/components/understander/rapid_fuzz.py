import os
import json

import typing
from rapidfuzz import fuzz

from backend.enums import Components
from backend.schemas import Context
from backend import config

class Rapidfuzz:

    def __init__(self, intents: typing.Dict):
        self.intents = intents

        self.conf_thresh = config.get(Components.Understander.value, 'config', 'conf_thresh')
        self.ratio = config.get(Components.Understander.value, 'config', 'ratio')
        self.ration_options = config.get(Components.Understander.value, 'config', 'ration_options')
        assert self.ratio in self.ration_options

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
        
        print(f'Skill: {skill}')
        print(f'Action: {action}')
        print(f'Conf: {conf}')

        if conf < self.conf_thresh:
            raise RuntimeError("Not confident in skill")
    
        return skill, action, conf

def build_engine(intents: typing.Dict) -> Rapidfuzz:
    return Rapidfuzz(intents)

def default_config() -> typing.Dict:
    return {
        "conf_thresh": 80,
        "ratio": "simple_ratio",
        "ration_options": [
            "simple_ratio",
            "partial_ratio",
            "token_sort_ratio",
            "token_set_ratio",
            "weighted_ratio",
            "quick_ratio"
        ]
    }