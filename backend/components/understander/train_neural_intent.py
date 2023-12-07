import os
import json
import pickle
import typing
import numpy as np

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator
from sklearn.metrics import precision_score, recall_score, f1_score

from backend.utils.nlp import clean_text, encode_word_vec, pad_sequence

def load_training_data(intents: typing.Dict):
    compiled_data = []
    for skill, patterns in intents.items():
        compiled_data.extend([[skill, clean_text(pattern)] for pattern in patterns])
    compiled_data = np.array(compiled_data)
    return compiled_data[:,1], compiled_data[:,0]

def train_classifier(X: typing.List, y: typing.List, model_file: str, vocab_file: str):

    print('Training classifier')

    # fix random seed for reproducibility
    np.random.seed(7)
    max_length = 10
    embedding_dim = 100

    labels = list(set(y))
    label_to_int = dict((l, i) for i, l in enumerate(labels))
    int_to_label = dict((i, l) for i, l in enumerate(labels))

    raw_text = ' '.join(X)
    words = sorted(list(set(raw_text.split())))
    word_to_int = dict((c, i+1) for i, c in enumerate(words))
    int_to_word = dict((i+1, c) for i, c in enumerate(words))
    word_to_int['BLANK'] = 0
    int_to_word[0] = 'BLANK'

    n_vocab = len(word_to_int)
    n_labels = len(labels)

    print('Word vocab size: ', n_vocab)
    print('Word to int: ', word_to_int)
    print('Number of total labels: ', n_labels)
    print('Labels: ', labels)

    pickle.dump([word_to_int, int_to_label, max_length], open(vocab_file, 'wb'))

    data_X = []
    data_y = []
    for text, label in zip(X, y):
        encoded = encode_word_vec(text, word_to_int)
        padded = pad_sequence(encoded, max_length)
        data_X.append(padded)
        data_y.append([label_to_int[label]])

    X = np.array(data_X)
    onehot_encoder = OneHotEncoder(sparse=False)
    y = onehot_encoder.fit_transform(data_y)
    y = np.array(y)

    print(X[0], y[0])

    model = Sequential()
    model.add(Embedding(n_vocab, embedding_dim, input_length=max_length))
    model.add(LSTM(32))
    #model.add(Dropout(0.2))
    model.add(Dense(n_labels, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    print(model.summary())
    model.fit(X, y, epochs=25, batch_size=16)

    scores = model.evaluate(X, y, verbose=0)
    print("Accuracy: %.2f%%" % (scores[1]*100))

    model.save(model_file)
