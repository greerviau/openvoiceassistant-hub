import os
import pickle
import numpy as np
from keras.models import load_model
from backend.utils.nlp import clean_text, encode_word_vec, pad_sequence
from backend.config import Configuration
from backend.components.understander.train_intent_model import train_classifier

class Classifier:
    def __init__(self, config: Configuration):
        self.config = config

        model_dump = config.get('model_dump')

        print('Loading classifier')
        intent_model = config.get('components', 'understander', 'model_file')
        if not intent_model:
            intent_model = os.path.join(model_dump, 'intent_model.h5')
            config.setkey('components', 'understander', 'model_file', value=intent_model)

        vocab_file = config.get('components', 'understander', 'vocab_file')
        if not vocab_file:
            vocab_file = os.path.join(model_dump, 'intent_vocab.p')
            config.setkey('components', 'understander', 'vocab_file', value=vocab_file)

        if not os.path.exists(intent_model) or not os.path.exists(vocab_file):
            print('Classifier model not found')
            print('Training classifier')
            imported_skills = config.get('components', 'skillset', 'imported_skills')
            skills_dir = os.path.join(config.get('base_dir'), 'skills')
            model_dump = config.get('model_dump')
            train_classifier(imported_skills, skills_dir, model_dump)

        self.conf_thresh = config.get('components', 'understander', 'conf_thresh')
        self.intent_model = load_model(intent_model)
        self.word_to_int, self.int_to_label, self.seq_length = pickle.load(open(vocab_file, 'rb'))

    def predict_intent(self, text):
        cleaned = clean_text(text)
        encoded = encode_word_vec(cleaned, self.word_to_int)
        padded = pad_sequence(encoded, self.seq_length)
        prediction = self.intent_model.predict(np.array([padded]))[0]
        argmax = np.argmax(prediction)
        label = self.int_to_label[argmax]
        skill, action = label.split('-')
        return skill, action, round(float(prediction[argmax])*100, 3)