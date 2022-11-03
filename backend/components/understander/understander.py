import typing
import time
import os
import pickle

from backend.config import Configuration
from backend.components.understander.classifier import Classifier
from backend.components.understander.train_intent_model import train_classifier, load_training_data
from backend.utils.nlp import clean_text
from backend.schemas import Context

class Understander:
    def __init__(self, config: Configuration):
        self.config = config

        self.load_classifier()

        self.wake_word = self.config.get('wake_word')
        self.engage_delay = self.config.get('engage_delay')

        self.conf_thresh = self.config.get('components', 'understander', 'conf_thresh')

    def load_classifier(self):
        model_dump = self.config.get('model_dump')

        print('Loading classifier')
        intent_model = self.config.get('components', 'understander', 'model_file')
        if not intent_model:
            intent_model = os.path.join(model_dump, 'intent_model.h5')
            self.config.setkey('components', 'understander', 'model_file', value=intent_model)

        vocab_file = self.config.get('components', 'understander', 'vocab_file')
        if not vocab_file:
            vocab_file = os.path.join(model_dump, 'intent_vocab.p')
            self.config.setkey('components', 'understander', 'vocab_file', value=vocab_file)

        imported_skills = self.config.get('components', 'skillset', 'imported_skills')
        skills_dir = os.path.join(self.config.get('base_dir'), 'skills')

        if not os.path.exists(intent_model) or not os.path.exists(vocab_file):
            print('Classifier model not found')
            X, y = load_training_data(imported_skills, skills_dir)
            train_classifier(X, y, model_dump)
        else:
            _, int_to_label, _ = pickle.load(open(vocab_file, 'rb'))
            n_labels = len(int_to_label)
            X, y = load_training_data(imported_skills, skills_dir)
            labels = list(set(y))
            if len(labels) != n_labels:
                print('Change to skills detected, retraining classifier')
                train_classifier(X, y, model_dump)
        
        self.classifier = Classifier(intent_model, vocab_file)

    def understand(self, command: str) -> typing.Tuple[str, str, float]:
        skill, action, conf = self.classifier.predict_intent(command)
        
        print(f'Skill: {skill}')
        print(f'Action: {action}')
        print(f'Conf: {conf}')
    
        return skill, action, conf
    
    def run_stage(self, context: Context):
        print('Understanding Stage')

        try:
            cleaned_command = context['cleaned_command']
        except KeyError:
            command = context['command']
            cleaned_command = clean_text(command)
            context['cleaned_command'] = cleaned_command
            print(f'Cleaned Command: {cleaned_command}')

        engage = context['engage']

        time_sent = context['time_sent']
        last_time_engaged = context['last_time_engaged']

        delta_time = time_sent - last_time_engaged

        start = time.time()

        if engage or delta_time < self.engage_delay:
            skill, action, conf = self.understand(cleaned_command)
            context['time_to_understand'] = time.time() - start
            context['skill'] = skill
            context['action'] = action
            context['conf'] = conf
            
            if conf < self.conf_thresh:
                raise RuntimeError('Not confident in skill')
        else:
            raise RuntimeError('Command does not engage')

