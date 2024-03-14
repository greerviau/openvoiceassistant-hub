import os
import pickle
import typing
import math
import logging
logger = logging.getLogger("components.understander.neural_intent")

import numpy as np

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader

from core import config
from core.dir import MODELDIR
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
    def __init__(self, dropout, hidden_dim, n_layers, vocab_size, num_classes):
        super(LargeIntentClassifier, self).__init__()
        self.hidden_dim = hidden_dim
        self.embedding = nn.Embedding(vocab_size, 100)
        self.lstm1 = nn.LSTM(100, hidden_dim, n_layers, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim*2, num_classes)
        self.drop = nn.Dropout(p=dropout)
        
    def forward(self, x):
        x = x.long()
        embed = self.embedding(x)
        out, _ = self.lstm(embed)
        out = torch.cat((out[:, -1, :self.hidden_dim], out[:, 0, self.hidden_dim:]), dim=1)
        out = self.drop(out)
        out = self.fc(out)
        return torch.nn.functional.softmax(out, dim=1)

class NeuralIntent:

    def __init__(self, algo_config: typing.Dict, intents: typing.Dict, ova: "OpenVoiceAssistant"):
        logger.info("Loading Neural Intent Classifier")
        self.ova = ova

        minimum_training_accuracy = algo_config["minimum_training_accuracy"]
        if minimum_training_accuracy > 100:
            minimum_training_accuracy = 100
            config.set(Components.Understander.value, "config", "minimum_training_accuracy", minimum_training_accuracy)
        elif minimum_training_accuracy < 0:
            minimum_training_accuracy = 0
            config.set(Components.Understander.value, "config", "minimum_training_accuracy", minimum_training_accuracy)

        logger.info(f"Minimum training accuracy: {minimum_training_accuracy}")

        dropout = algo_config["dropout"]
        if dropout > 1:
            dropout = 1
            config.set(Components.Understander.value, "config", "dropout", dropout)
        elif dropout < 0:
            dropout = 0
            config.set(Components.Understander.value, "config", "dropout", dropout)

        logger.info(f"Model dropout: {dropout}")

        batch_size = algo_config["batch_size"]
        if batch_size > 64:
            batch_size = 64
            config.set(Components.Understander.value, "config", "batch_size", batch_size)
        elif batch_size < 8:
            batch_size = 8
            config.set(Components.Understander.value, "config", "batch_size", batch_size)

        logger.info(f"Batch size: {batch_size}")

        use_gpu = algo_config["use_gpu"]
        use_gpu = torch.cuda.is_available() and use_gpu
        config.set(Components.Transcriber.value, "config", "use_gpu", use_gpu)

        self.device = torch.device("cuda" if use_gpu else "cpu")
        logger.info(f"Using device: {self.device}")

        model_file = os.path.join(MODELDIR, "neural_intent_model.pt")
        vocab_file = os.path.join(MODELDIR, "neural_intent_vocab.p")

        x, y, self.max_length = load_training_data(intents)
        labels = list(set(y))
        logger.info(f"Intents : {labels}")

        self.network_size = algo_config["network_size"]
        logger.info(f"Using {self.network_size} network")

        if self.network_size == "small":
            hidden_dim = 32
            n_layers = 1
        if self.network_size == "medium":
            hidden_dim = 64
            n_layers = 1
        else:
            hidden_dim = 64
            n_layers = 2
        
        retrain = algo_config["retrain"]
        if os.path.exists(vocab_file):
            self.word_to_int, int_to_word, label_to_int, self.int_to_label, n_vocab, n_labels, loaded_labels, self.max_length = pickle.load(open(vocab_file, "rb"))

        if retrain or not os.path.exists(vocab_file) or not os.path.exists(model_file) or sorted(labels) != sorted(loaded_labels):
            logger.info("Retraining Neural Intent Model")

            try: os.remove(model_file)
            except: pass
            try: os.remove(vocab_file)
            except: pass

            label_to_int, self.int_to_label, self.word_to_int, int_to_word, n_vocab, n_labels = build_vocab(x, y)
            pickle.dump([self.word_to_int, int_to_word, label_to_int, self.int_to_label, n_vocab, n_labels, labels, self.max_length], open(vocab_file, "wb"))
            X, Y = preprocess_data(x, y, self.word_to_int, self.max_length, label_to_int)

            self.intent_model = IntentClassifier(dropout, hidden_dum, n_layers, n_vocab, n_labels).to(self.device)
            train_classifier(X, Y, minimum_training_accuracy, batch_size, self.intent_model, model_file, self.device)
            config.set(Components.Understander.value, "config", "retrain", False)
        else:
            self.intent_model = IntentClassifier(dropout, hidden_dum, n_layers, n_vocab, n_labels).to(self.device)

        self.intent_model.eval()

    def predict_intent(self, text: str) -> typing.Tuple[str, str, float]:
        encoded = encode_word_vec(text, self.word_to_int)
        padded = pad_sequence(encoded, self.max_length)
        with torch.no_grad():
            inputs = torch.LongTensor(np.array([padded])).to(self.device)
            prediction = self.intent_model(inputs)
            conf, idx = torch.max(prediction, dim=1)
            label = self.int_to_label[idx.item()]
            skill, action = label.split("-")
            return skill, action, round(float(conf.item()) * 100, 3)

    def understand(self, context: Context) -> typing.Tuple[str, str, float]:
        encoded_command = context["encoded_command"]
        return self.predict_intent(encoded_command)

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
    logger.info(f"Max sequence length: {max_length}")
    return x, y, max_length

def build_vocab(X: np.array, y: np.array):
    logger.info("Building vocab")

    labels = list(set(y))
    label_to_int = dict((l, i) for i, l in enumerate(labels))
    int_to_label = dict((i, l) for i, l in enumerate(labels))

    raw_text = " ".join(X)
    words = sorted(list(set(raw_text.split())))
    word_to_int = dict((c, i+1) for i, c in enumerate(words))
    int_to_word = dict((i+1, c) for i, c in enumerate(words))
    word_to_int["BLANK"] = 0
    int_to_word[0] = "BLANK"

    n_vocab = len(word_to_int)
    n_labels = len(labels)

    logger.info(f"N vocab: {n_vocab}")
    logger.info(f"N labels: {n_labels}")

    return label_to_int, int_to_label, word_to_int, int_to_word, n_vocab, n_labels

def preprocess_data(x, y, word_to_int, max_length, label_to_int):
    logger.info("Preprocessing data")
    data_x = []
    data_y = []
    for text, label in zip(x, y):
        encoded = encode_word_vec(text, word_to_int)
        padded = pad_sequence(encoded, max_length)
        data_x.append(padded)
        data_y.append(label_to_int[label])

    X = np.array(data_x)
    Y = np.array(data_y, dtype=np.int64)

    logger.info(f"N Samples: {len(X)}")
    logger.info(f"X shape: {X.shape}")
    logger.info(f"Y shape: {Y.shape}")

    return X, Y
    
def train_classifier(X, Y, minimum_training_accuracy, batch_size, model, model_file, device):

    def weight_reset(m):
        if isinstance(m, nn.LSTM) or isinstance(m, nn.Linear):
            m.reset_parameters()

    # Convert X and Y to PyTorch tensors and move them to the specified device
    X_tensor = torch.tensor(X).to(device)
    Y_tensor = torch.tensor(Y).to(device)

    logger.info("Training classifier")

    # Training parameters
    learning_rate = 0.001

    # Create data loaders for the training and validation sets
    train_dataset = IntentDataset(X_tensor, Y_tensor)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    model.train()

    # Define the loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    
    trained = False
    while not trained:
        num_epochs = 40
        try:
            model.apply(weight_reset)
            optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
            # Iterate over the training data for the specified number of epochs
            epoch = 0
            accuracy = 0
            while accuracy < minimum_training_accuracy:
                if num_epochs > 200:
                    raise RuntimeError("Failed to train Neural Intent model")
                    
                while epoch <= num_epochs:
                    epoch += 1
                    total_loss = 0.0
                    total_samples = 0
                    correct = 0

                    for x_batch, y_batch in train_loader:
                        optimizer.zero_grad()
                        x = x_batch.to(device)
                        y = y_batch.to(device)  # Move data to GPU
                        y_pred = model(x)
                        loss = criterion(y_pred, y)
                        loss.backward()
                        optimizer.step()

                        total_loss += loss.item() * len(x)
                        total_samples += len(x)

                        # Calculate accuracy
                        _, predicted = torch.max(y_pred, 1)
                        correct += (predicted == y).sum().item()

                    avg_loss = total_loss / total_samples
                    accuracy = 100 * correct / total_samples
                    
                    if epoch % 10 == 0:
                        logger.info(f"Epoch {epoch}/{num_epochs} | Train Loss: {avg_loss:.4f} | Accuracy: {accuracy:.2f}%")
                
                num_epochs += 20

            torch.save(model.state_dict(), model_file)
            trained = True
        except RuntimeError:
            logger.error("Failed to train neural intent model, retrying...")
        
def build_engine(algo_config: typing.Dict, intents: typing.Dict, ova: "OpenVoiceAssistant") -> NeuralIntent:
    return NeuralIntent(algo_config, intents, ova)

def default_config() -> typing.Dict:
    return {
        "id": "neural_intent",
        "use_gpu": False,
        "retrain": False,
        "minimum_training_accuracy": 80,
        "network_size": "small",
        "network_size_options": [
            "small",
            "medium",
            "large"
        ],
        "dropout": 0.5,
        "batch_size": 8
    }