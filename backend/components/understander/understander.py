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
        self.ova = ova
        imported_skills = list(config.get('skills').keys())
        self.intents = self.load_intents(imported_skills)
        self.vocab_list = self.load_vocab(self.intents.values())
        self.engage_delay = config.get("engage_delay")
    
        self.algo = config.get(Components.Understander.value, "algorithm").lower().replace(" ", "_")
        self.module = importlib.import_module(f"backend.components.understander.{self.algo}")

        self.verify_config()

        self.engine = self.module.build_engine(ova, self.intents)

    def verify_config(self):
        current_config = config.get(Components.Understander.value, 'config')
        default_config = self.module.default_config()
        try:
            if not current_config or (current_config.keys() != default_config.keys()) or current_config["id"] != default_config["id"]:
                raise Exception("Incorrect config")
        except:
            config.set(Components.Understander.value, 'config', default_config)

    def load_intents(self, imported_skills: List):
        tagged_intents = {}
        for skill in imported_skills:
            intents = self.ova.skill_manager.get_skill_intents(skill)
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
        start = time.time()

        time_sent = context["time_sent"]
        last_time_engaged = context["last_time_engaged"]

        delta_time = time_sent - last_time_engaged
        
        command = context["command"]

        try:
            cleaned_command = context["cleaned_command"]
        except KeyError:
            cleaned_command = clean_text(command)
            context["cleaned_command"] = cleaned_command
            print(f"Cleaned Command: {cleaned_command}")
        
        context["pos_info"] = information_extraction(cleaned_command)

        encoded_command = encode_command(cleaned_command, self.vocab_list)
        context["encoded_command"] = encoded_command
        print(f"Encoded command: {encoded_command}")
        
        if encoded_command in ["", "BLANK"] or cleaned_command in ["stop", "cancel", "nevermind", "forget it"]:
            skill = "NO_COMMAND"
            action = ""
            conf = 100
            pass_threshold = True
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
                skill, action, conf, pass_threshold = self.engine.understand(context)
        
        print(f'Skill: {skill}')
        print(f'Action: {action}')
        print(f'Conf: {conf}')
        context["skill"] = skill
        context["action"] = action
        context["conf"] = conf
        context["pass_threshold"] = pass_threshold

        dt = time.time() - start
        context["time_to_understand"] = dt
        print("Time to understand: ", dt)

