import os
import json

from typing import List, Dict
from rapidfuzz import fuzz

from backend.enums import Components
from backend.schemas import Context
from backend import config

class Fuzzy:

    def __init__(self):
        imported_skills = config.get('components', Components.Skillset.value, 'imported_skills')
        skills_dir = os.path.join(config.get('base_dir'), 'skills')
        self.intents = self.load_intents(imported_skills, skills_dir)

        self.conf_thresh = config.get('components', Components.Understander.value, 'config', 'conf_thresh')

    def load_intents(self, imported_skills: List, skills_dir: str):
        tagged_intents = {}
        for skill in imported_skills:
            intents = json.load(open(os.path.join(skills_dir, skill, 'intents.json')))['intentions']
            for intent in intents:
                tag = intent['action']
                patterns = intent['patterns']
                label = f'{skill}-{tag}'
                tagged_intents[label] = patterns
        return tagged_intents

    def understand(self, context: Context):
        command = context['cleaned_command']
        
        conf = 0
        intent = None
        for label, patterns in self.intents.items():
            for pattern in patterns:
                r = fuzz.partial_ratio(command, pattern)
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

def build_engine() -> Fuzzy:
    return Fuzzy()

def default_config() -> Dict:
    return {
        "conf_thresh": 80
    }