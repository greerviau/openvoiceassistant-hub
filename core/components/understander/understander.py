import time
import importlib
import typing
import random

from core.enums import Components
from core import config
from core.schemas import Context
from core.utils.nlp.preprocessing import clean_text, encode_command
from core.utils.nlp.information_extraction import extract_information
from core.utils.nlp.false_positives import FALSE_POSITIVES, add_false_positive

class Understander:
    def __init__(self, ova: "OpenVoiceAssistant"):
        self.ova = ova
        imported_skills = list(config.get('skills').keys())
        self.intents, n_samples = self.load_intents(imported_skills)
        self.vocab_list = self.load_vocab(self.intents.values())
        self.add_negative_samples(n_samples)
        self.engage_delay = config.get("engage_delay")
    
        self.algo = config.get(Components.Understander.value, "algorithm").lower().replace(" ", "_")
        self.module = importlib.import_module(f"core.components.understander.{self.algo}")

        self.verify_config()

        self.engine = self.module.build_engine(ova, self.intents)

    def verify_config(self):
        current_config = config.get(Components.Understander.value, 'config')
        default_config = self.module.default_config()
        try:
            if not current_config or (current_config.keys() != default_config.keys()) or current_config["id"] != default_config["id"]:
                raise RuntimeError("Incorrect config")
        except:
            config.set(Components.Understander.value, 'config', default_config)

    def load_intents(self, imported_skills: typing.List):
        tagged_intents = {}
        pattern_count = 0
        for skill in imported_skills:
            intents = self.ova.skill_manager.get_skill_intents(skill).copy()
            for intent in intents:
                tag = intent['action']
                print(tag)
                patterns = intent['patterns'].copy()
                print(len(patterns))
                #patterns.extend([f"BLANK {pattern}" for pattern in patterns])
                pattern_count += len(patterns)
                label = f'{skill}-{tag}'
                tagged_intents[label] = patterns
        
        print(f'N Positive Samples: {pattern_count}')
        return tagged_intents, pattern_count

    def add_negative_samples(self, n_samples: int):
        false_positives = list(set([encode_command(sample, self.vocab_list) for sample in FALSE_POSITIVES]))
        random.shuffle(false_positives)
        n_false_samples = n_samples
        if len(false_positives) > n_false_samples:
            false_samples = false_positives[:n_false_samples]
        else:
            false_samples = false_positives
        print(f'N Negative Samples: {len(false_samples)}')
        self.intents["NO_COMMAND-NO_ACTION"] = false_samples
    
    def load_vocab(self, patterns: typing.List[typing.List[str]]):
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
    
    def get_algorithm_default_config(self, algorithm_id: str) -> typing.Dict:
        try:
            module = importlib.import_module(f'core.components.understander.{algorithm_id}')
            return module.default_config()
        except Exception as e:
            raise RuntimeError('Understander algorithm does not exist')

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
        
        context["pos_info"] = extract_information(cleaned_command)

        encoded_command = encode_command(cleaned_command, self.vocab_list)
        context["encoded_command"] = encoded_command
        print(f"Encoded command: {encoded_command}")
        
        if encoded_command in ["", "BLANK"]:
            skill = "NO_COMMAND"
            action = "NO_ACTION"
            conf = 100
            pass_threshold = False
        else:
            hub_callback = context["hub_callback"] if "hub_callback" in context else None
            if hub_callback:
                try:
                    skill, action = hub_callback.split('.')
                    conf = 100
                    context["hub_callback"] = ''
                    pass_threshold = True
                except:
                    raise RuntimeError("Failed to parse callback")
            else:
                skill, action, conf, pass_threshold = self.engine.understand(context)
                if skill in ['NO_COMMAND'] or action in ['NO_ACTION']:
                    pass_threshold = False
                    add_false_positive(cleaned_command)
        
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
