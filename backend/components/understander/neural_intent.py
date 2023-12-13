import os
import pickle
import typing

import numpy as np

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import OneHotEncoder

from backend import config
from backend.schemas import Context
from backend.enums import Components
from backend.utils.nlp import clean_text

def encode_word_vec(text, vocab):
    encoded = np.zeros(len(text.split()))
    for i, word in enumerate(text.split()):
        if word in vocab.keys():
            encoded[i] = vocab[word]
    return np.array(encoded)

def pad_sequence(encoded, seq_length):
    padding = np.zeros(seq_length)
    if len(encoded) > seq_length:
        padding = encoded[:seq_length]
    else:
        padding[:len(encoded)] = encoded
    return padding

class NeuralIntent:

    def __init__(self, ova: 'OpenVoiceAssistant', intents: typing.Dict):
        embedding_dim = 100
        hidden_dim = 64

        self.ova = ova
        model_dump = self.ova.model_dump

        print('Loading classifier')
        model_file = os.path.join(model_dump, 'neural_intent_model.pt')
        vocab_file = os.path.join(model_dump, 'neural_intent_vocab.p')

        x, y, self.max_length = load_training_data(intents)
        labels = list(set(y))

        if not os.path.exists(vocab_file):
            print('Vocab file not found')
            label_to_int, self.int_to_label, self.word_to_int, int_to_word, n_vocab, n_labels = build_vocab(x, y)
            pickle.dump([self.word_to_int, int_to_word, label_to_int, self.int_to_label, n_vocab, n_labels, labels, self.max_length], open(vocab_file, 'wb'))  
        else:
            self.word_to_int, int_to_word, label_to_int, self.int_to_label, n_vocab, n_labels, loaded_labels, self.max_length = pickle.load(open(vocab_file, 'rb'))

        if not os.path.exists(model_file) or sorted(labels) != sorted(loaded_labels):
            print('Model file not found')
            X, Y = preprocess_data(x, y, self.word_to_int, self.max_length, label_to_int)
            train_classifier(X, Y, embedding_dim, hidden_dim, n_labels, n_vocab, model_file)
        
        self.intent_model = IntentClassifier(n_vocab, embedding_dim, hidden_dim, n_labels)
        self.intent_model.load_state_dict(torch.load(model_file))
        self.intent_model.eval()

        self.conf_thresh = config.get(Components.Understander.value, 'config', 'conf_thresh')

    def predict_intent(self, text: str) -> typing.Tuple[str, str, float]:
        encoded = encode_word_vec(text, self.word_to_int)
        padded = pad_sequence(encoded, self.max_length)
        with torch.no_grad():
            inputs = torch.LongTensor(np.array([padded]))
            prediction = self.intent_model(inputs)
            argmax = torch.argmax(prediction, dim=1).item()
            conf = torch.max(prediction, dim=1)[0]
            label = self.int_to_label[argmax]
            skill, action = label.split('-')
            return skill, action, round(float(conf)*100, 3)

    def understand(self, context: Context) -> typing.Tuple[str, str, float]:
        encoded_command = context['encoded_command']
        skill, action, conf = self.predict_intent(encoded_command)
        
        print(f'Skill: {skill}')
        print(f'Action: {action}')
        print(f'Conf: {conf}')

        if conf < self.conf_thresh:
            raise RuntimeError("Not confident in skill")
    
        return skill, action, conf
    
class IntentDataset(Dataset):
    def __init__(self, X, Y):
        self.x = X
        self.y = Y
        
    def __len__(self):
        return len(self.x)
    
    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]   
    
class IntentClassifier(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_classes):
        super(IntentClassifier, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, num_classes)
        
    def forward(self, x):
        embed = self.embedding(x)
        out, _ = self.lstm(embed)
        out = out[:, -1, :]
        out = self.fc(out)
        return torch.nn.functional.softmax(out, dim=1)
    
def load_training_data(intents: typing.Dict):
    print("Loading data")
    compiled_data = []
    max_length = 0
    for label, patterns in intents.items():
        for pattern in patterns:
            pattern = clean_text(pattern)
            if len(pattern.split()) > max_length:
                max_length = len(pattern.split())
            compiled_data.append([pattern, label])
    compiled_data = np.array(compiled_data)
    x = compiled_data[:,0]
    y = compiled_data[:,1]
    print("Max sequence length: ", max_length)
    return x, y, max_length

def build_vocab(X: np.array, y: np.array):
    print("Building vocab")

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

    print('N vocab: ', n_vocab)
    print('N labels: ', n_labels)

    return label_to_int, int_to_label, word_to_int, int_to_word, n_vocab, n_labels

def preprocess_data(x, y, word_to_int, max_length, label_to_int):
    print("Preprocessing data")
    data_x = []
    data_y = []
    for text, label in zip(x, y):
        encoded = encode_word_vec(text, word_to_int)
        padded = pad_sequence(encoded, max_length)
        data_x.append(padded)
        data_y.append([label_to_int[label]])

    X = np.array(data_x)
    onehot_encoder = OneHotEncoder(sparse=False)
    Y = onehot_encoder.fit_transform(data_y)
    Y = np.array(Y)

    print(X[0], Y[0])

    return X, Y
    
def train_classifier(X, Y, embedding_dim, hidden_dim, num_classes, vocab_size, model_file):
    print('Training classifier')
    # Training parameters
    batch_size = 8
    num_epochs = 50
    learning_rate = 0.001

    # Create the model
    model = IntentClassifier(vocab_size, embedding_dim, hidden_dim, num_classes)

    # Define the loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # Create data loaders for the training and validation sets
    train_dataset = IntentDataset(X, Y)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    # Iterate over the training data for the specified number of epochs
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0.0
        total_samples = 0
        for x_batch, y_batch in train_loader:
            x = x_batch.type(torch.LongTensor)
            y = y_batch.type(torch.FloatTensor)
            y_pred = model(x)
            loss = criterion(y_pred, y)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            total_loss += loss.item() * len(x)
            total_samples += len(x)

        avg_loss = total_loss / total_samples

        print(f"Epoch {epoch+1}/{num_epochs}, Train Loss: {avg_loss:.4f}")

    torch.save(model.state_dict(), model_file)
        
def build_engine(ova: 'OpenVoiceAssistant', intents: typing.Dict) -> NeuralIntent:
    return NeuralIntent(ova, intents)

def default_config() -> typing.Dict:
    return {
        "neural_intent": True,
        "conf_thresh": 80
    }