import os
import json

from typing import List, Dict
from rapidfuzz import fuzz

from backend.utils.nlp import clean_text
from backend.enums import Components
from backend.schemas import Context
from backend import config

class Fuzzy:

    def __init__(self, intents: Dict):
        self.intents = intents

        self.conf_thresh = config.get(Components.Understander.value, 'config', 'conf_thresh')

    def understand(self, context: Context):
        encoded_command = context['encoded_command']

        conf = 0
        intent = None
        for label, patterns in self.intents.items():
            for pattern in patterns:
                r = fuzz.partial_ratio(encoded_command, pattern)
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

def build_engine(intents: Dict) -> Fuzzy:
    return Fuzzy(intents)

def default_config() -> Dict:
    return {
        "conf_thresh": 80,
        "ratio": "simple_ratio",
        "ration_options": [
            "simple_ration",
            "partial_ratio",
            "token_sort_ratio",
            "token_set_ratio",
            "weighted_ratio",
            "quick_ratio"
        ]
    }