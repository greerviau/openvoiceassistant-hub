import os
import pickle
import numpy as np
from keras.models import load_model
from utils.nlp import clean_text, encode_word_vec, pad_sequence

class Classifier:
    def __init__(self, config):
        intent_model = config['intent_model']
        vocab_file = config['vocab_file']
        print ('i\'m a silly little slut')
        self.intent_model = load_model(intent_model)
        self.word_to_int, self.int_to_label, self.seq_length = pickle.load(open(vocab_file, 'rb'))
        self.CONF_THRESH = 85

    def predict_intent(self, text):
        cleaned = clean_text(text)
        encoded = encode_word_vec(cleaned, self.word_to_int)
        padded = pad_sequence(encoded, self.seq_length)
        prediction = self.intent_model.predict(np.array([padded]))[0]
        argmax = np.argmax(prediction)
        label = self.int_to_label[argmax]
        skill, action = label.split('-')
        return skill, action, round(float(prediction[argmax])*100, 3)