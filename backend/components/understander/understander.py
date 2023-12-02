import time
import importlib
import os
import json
from typing import List

from backend.enums import Components
from backend import config
from backend.utils.nlp import clean_text
from backend.schemas import Context
from backend.utils.nlp import information_extraction, encode_command

class Understander:
    def __init__(self, ova: "OpenVoiceAssistant"):
        imported_skills = config.get(Components.Skillset.value, 'imported_skills')
        skills_dir = os.path.join(config.get('base_dir'), 'skills')
        self.intents = self.load_intents(imported_skills, skills_dir)
        self.vocab_list = self.load_vocab(self.intents.values())
        self.engage_delay = config.get("engage_delay")
    
        self.algo = config.get(Components.Understander.value, "algorithm").lower().replace(" ", "_")
        self.module = importlib.import_module(f"backend.components.understander.{self.algo}")

        self.verify_config()

        self.engine = self.module.build_engine(self.intents)

    def verify_config(self):
        current_config = config.get(Components.Understander.value, 'config')
        default_config = self.module.default_config()
        if not current_config or (current_config.keys() != default_config.keys()):
            config.set(Components.Understander.value, 'config', default_config)

    def load_intents(self, imported_skills: List, skills_dir: str):
        tagged_intents = {}
        for skill in imported_skills:
            intents = json.load(open(os.path.join(skills_dir, skill.replace('.', '/'), 'intents.json')))['intentions']
            for intent in intents:
                tag = intent['action']
                patterns = intent['patterns']
                label = f'{skill}-{tag}'
                tagged_intents[label] = patterns
        return tagged_intents
    
    def load_vocab(self, patterns: List[List[str]]):
        all_words = []
        for pattern_list in patterns:
            all_words.extend(pattern_list)
        all_words = ' '.join(all_words)
        unique = []
        for word in all_words.split():
            word = clean_text(word)
            if word not in unique:
                unique.append(word)
        return unique
    
    def run_stage(self, context: Context):
        print("Understanding Stage")

        time_sent = context["time_sent"]
        last_time_engaged = context["last_time_engaged"]

        delta_time = time_sent - last_time_engaged
        
        start = time.time()
        
        command = context["command"]

        context["pos_info"] = information_extraction(command)

        try:
            cleaned_command = context["cleaned_command"]
        except KeyError:
            cleaned_command = clean_text(command)
            context["cleaned_command"] = cleaned_command
            print(f"Cleaned Command: {cleaned_command}")

        encoded_command = encode_command(cleaned_command, self.vocab_list)
        context["encoded_command"] = encoded_command
        print(f"Encoded command: {encoded_command}")
        
        if encoded_command in ["", "BLANK"]:
            skill = "NO_COMMAND"
            action = ""
            conf = 100
        else:
            hub_callback = context["hub_callback"] if "hub_callback" in context else None
            if hub_callback:
                try:
                    skill, action = hub_callback.split('.')
                    conf = 100
                    context["hub_callback"] = ''
                except:
                    raise RuntimeError("Failed to parse callback")
            else:
                try:
                    skill, action, conf = self.engine.understand(context)
                except RuntimeError:
                    skill = "DID_NOT_UNDERSTAND"
                    action = ''
                    conf = 100

        context["time_to_understand"] = time.time() - start
        context["skill"] = skill
        context["action"] = action
        context["conf"] = conf

