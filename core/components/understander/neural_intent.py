import os
import pickle
import typing
import math

import numpy as np

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader

from core import config
from core.schemas import Context
from core.enums import Components
from core.utils.nlp.preprocessing import clean_text

class IntentDataset(Dataset):
    def __init__(self, X, Y):
        self.x = X
        self.y = Y
        
    def __len__(self):
        return len(self.x)
    
    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]   
    
class IntentClassifier(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim_1, hidden_dim_2, num_classes):
        super(IntentClassifier, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm1 = nn.LSTM(embedding_dim, hidden_dim_1, batch_first=True)
        self.lstm2 = nn.LSTM(hidden_dim_1, hidden_dim_2, batch_first=True)
        self.fc = nn.Linear(hidden_dim_1, num_classes)
        self.drop = nn.Dropout(p=0.2)
        
    def forward(self, x):
        embed = self.embedding(x)
        out, _ = self.lstm1(embed)
        #out, _ = self.lstm2(out)
        out = out[:, -1, :]
        out = self.drop(out)
        out = self.fc(out)
        return torch.nn.functional.softmax(out, dim=1)

class NeuralIntent:

    def __init__(self, ova: 'OpenVoiceAssistant', intents: typing.Dict):
        print("Loading Neural Intent Classifier")
        self.ova = ova
        model_dump = self.ova.model_dump

        retrain = config.get(Components.Understander.value, 'config', 'retrain')

        embedding_dim = 100
        hidden_dim_1 = 64
        hidden_dim_2 = 32

        model_file = os.path.join(model_dump, 'neural_intent_model.pt')
        vocab_file = os.path.join(model_dump, 'neural_intent_vocab.p')

        x, y, self.max_length = load_training_data(intents)
        labels = list(set(y))
        print(f"Intents : {labels}")
 
        if os.path.exists(vocab_file):
            self.word_to_int, int_to_word, label_to_int, self.int_to_label, n_vocab, n_labels, loaded_labels, self.max_length = pickle.load(open(vocab_file, 'rb'))

        if retrain or not os.path.exists(vocab_file) or not os.path.exists(model_file) or sorted(labels) != sorted(loaded_labels):
            print("Retraining Neural Intent Model")

            try: os.remove(model_file)
            except: pass
            try: os.remove(vocab_file)
            except: pass

            label_to_int, self.int_to_label, self.word_to_int, int_to_word, n_vocab, n_labels = build_vocab(x, y)
            pickle.dump([self.word_to_int, int_to_word, label_to_int, self.int_to_label, n_vocab, n_labels, labels, self.max_length], open(vocab_file, 'wb'))
            X, Y = preprocess_data(x, y, self.word_to_int, self.max_length, label_to_int)
            train_classifier(X, Y, n_vocab, embedding_dim, hidden_dim_1, hidden_dim_2, n_labels, model_file)
            config.set(Components.Understander.value, 'config', 'retrain', False)
            
        self.intent_model = IntentClassifier(n_vocab, embedding_dim, hidden_dim_1, hidden_dim_2, n_labels)
        self.intent_model.load_state_dict(torch.load(model_file))
        self.intent_model.eval()

        self.conf_thresh = config.get(Components.Understander.value, 'config', 'conf_thresh')

    def predict_intent(self, text: str) -> typing.Tuple[str, str, float]:
        encoded = encode_word_vec(text, self.word_to_int)
        padded = pad_sequence(encoded, self.max_length)
        with torch.no_grad():
            inputs = torch.LongTensor(np.array([padded]))
            prediction = self.intent_model(inputs)
            conf, idx = torch.max(prediction, dim=1)
            label = self.int_to_label[idx.item()]
            skill, action = label.split('-')
            return skill, action, round(float(conf.item()) * 100, 3)

    def understand(self, context: Context) -> typing.Tuple[str, str, float]:
        encoded_command = context['encoded_command']
        skill, action, conf = self.predict_intent(encoded_command)
        
        pass_threshold = True
        if conf < self.conf_thresh:
            pass_threshold = False
    
        return skill, action, conf, pass_threshold

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
    
def load_training_data(intents: typing.Dict):
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

    print(f'N vocab: {n_vocab}')
    print(f'N labels: {n_labels}')

    return label_to_int, int_to_label, word_to_int, int_to_word, n_vocab, n_labels

def preprocess_data(x, y, word_to_int, max_length, label_to_int):
    print("Preprocessing data")
    data_x = []
    data_y = []
    for text, label in zip(x, y):
        encoded = encode_word_vec(text, word_to_int)
        padded = pad_sequence(encoded, max_length)
        data_x.append(padded)
        data_y.append(label_to_int[label])

    X = np.array(data_x)
    Y = np.array(data_y, dtype=np.int64)

    print(f"N Samples: {len(X)}")
    print(f"X shape: {X.shape}")
    print(f"Y shape: {Y.shape}")

    return X, Y
    
def train_classifier(X, Y, n_vocab, embedding_dim, hidden_dim_1, hidden_dim_2, n_labels, model_file):
    print('Training classifier')
    # Training parameters
    batch_size = 16
    learning_rate = 0.001

    # Create data loaders for the training and validation sets
    train_dataset = IntentDataset(X, Y)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    trained = False
    while not trained:
        num_epochs = 50
        try:
            model = IntentClassifier(n_vocab, embedding_dim, hidden_dim_1, hidden_dim_2, n_labels)
            # Define the loss function and optimizer
            criterion = nn.CrossEntropyLoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

            # Iterate over the training data for the specified number of epochs
            epoch = 0
            accuracy = 0
            while accuracy < 95:
                if num_epochs > 150:
                    raise RuntimeError("Failed to train Neural Intent model")
                while epoch <= num_epochs:
                    epoch += 1
                    model.train()
                    total_loss = 0.0
                    total_samples = 0
                    correct = 0

                    for x_batch, y_batch in train_loader:
                        x = x_batch.type(torch.LongTensor)
                        y = y_batch.type(torch.LongTensor)  # Use LongTensor for integer labels
                        y_pred = model(x)
                        loss = criterion(y_pred, y)
                        loss.backward()
                        optimizer.step()
                        optimizer.zero_grad()

                        total_loss += loss.item() * len(x)
                        total_samples += len(x)

                        # Calculate accuracy
                        _, predicted = torch.max(y_pred, 1)
                        correct += (predicted == y).sum().item()

                    avg_loss = total_loss / total_samples
                    accuracy = 100 * correct / total_samples

                    print(f"Epoch {epoch}/{num_epochs} | Train Loss: {avg_loss:.4f} | Accuracy: {accuracy:.2f}%")
                num_epochs += 20

            torch.save(model.state_dict(), model_file)
            trained = True
        except RuntimeError:
            print("Failed to train classifier, retrying")
        
def build_engine(ova: 'OpenVoiceAssistant', intents: typing.Dict) -> NeuralIntent:
    return NeuralIntent(ova, intents)

def default_config() -> typing.Dict:
    return {
        "id": "neural_intent",
        "conf_thresh": 80,
        "retrain": False
    }