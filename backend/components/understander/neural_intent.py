import os
import pickle

import numpy as np

from typing import Tuple, Dict
from keras.models import load_model

from backend.schemas import Context
from backend import config

from backend.enums import Components
from backend.components.understander.train_neural_intent_model import train_classifier, load_training_data
from backend.utils.nlp import clean_text, encode_word_vec, pad_sequence

class NeuralIntent:

    def __init__(self):
        self.load_classifier()

    
    def load_classifier(self):
        model_dump = config.get('model_dump')

        print('Loading classifier')
        model_file = config.get('components', Components.Understander.value, 'model_file')
        if not model_file:
            model_file = os.path.join(model_dump, 'intent_model.h5')
            config.set('components', Components.Understander.value, 'model_file', model_file)

        vocab_file = config.get('components', Components.Understander.value, 'vocab_file')
        if not vocab_file:
            vocab_file = os.path.join(model_dump, 'intent_vocab.p')
            config.set('components', Components.Understander.value, 'vocab_file', vocab_file)

        imported_skills = config.get('components', Components.Skillset.value, 'imported_skills')
        skills_dir = os.path.join(config.get('base_dir'), 'skills')

        if not os.path.exists(model_file) or not os.path.exists(vocab_file):
            print('Classifier model not found')
            X, y = load_training_data(imported_skills, skills_dir)
            train_classifier(X, y, model_file, vocab_file)
        else:
            _, int_to_label, _ = pickle.load(open(vocab_file, 'rb'))
            n_labels = len(int_to_label)
            X, y = load_training_data(imported_skills, skills_dir)
            labels = list(set(y))
            if len(labels) != n_labels:
                print('Change to skills detected, retraining classifier')
                train_classifier(X, y, model_file, vocab_file)
        
        self.intent_model = load_model(model_file)
        self.word_to_int, self.int_to_label, self.seq_length = pickle.load(open(vocab_file, 'rb'))

        self.conf_thresh = config.get('components', Components.Understander.value, 'config', 'conf_thresh')

    def predict_intent(self, text: str) -> Tuple[str, str, float]:
        cleaned = clean_text(text)
        encoded = encode_word_vec(cleaned, self.word_to_int)
        padded = pad_sequence(encoded, self.seq_length)
        prediction = self.intent_model.predict(np.array([padded]))[0]
        argmax = np.argmax(prediction)
        label = self.int_to_label[argmax]
        skill, action = label.split('-')
        return skill, action, round(float(prediction[argmax])*100, 3)

    def understand(self, context: Context) -> Tuple[str, str, float]:
        command = context['cleaned_command']
        skill, action, conf = self.predict_intent(command)
        
        print(f'Skill: {skill}')
        print(f'Action: {action}')
        print(f'Conf: {conf}')

        if conf < self.conf_thresh:
            raise RuntimeError("Not confident in skill")
    
        return skill, action, conf
        

def build_engine() -> NeuralIntent:
    return NeuralIntent()

def default_config() -> Dict:
    return {
        "vocab_file": "",
        "model_file": "",
        "conf_thresh": 80
    }