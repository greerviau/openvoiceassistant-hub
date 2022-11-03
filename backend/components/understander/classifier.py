import os
import pickle
import typing
import numpy as np

from backend.config import Configuration
from keras.models import load_model
from backend.utils.nlp import clean_text, encode_word_vec, pad_sequence

class Classifier:
    def __init__(self, intent_model: str, vocab_file: str):
        self.intent_model = load_model(intent_model)
        self.word_to_int, self.int_to_label, self.seq_length = pickle.load(open(vocab_file, 'rb'))

    def predict_intent(self, text: str) -> typing.Tuple[str, str, float]:
        cleaned = clean_text(text)
        encoded = encode_word_vec(cleaned, self.word_to_int)
        padded = pad_sequence(encoded, self.seq_length)
        prediction = self.intent_model.predict(np.array([padded]))[0]
        argmax = np.argmax(prediction)
        label = self.int_to_label[argmax]
        skill, action = label.split('-')
        return skill, action, round(float(prediction[argmax])*100, 3)