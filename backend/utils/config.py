import os
import json

DEFAULT_CONFIG = {
        "wake_word": "computer",
        "title": "",
        "engage_delay": 30,
        "nodes": {},
        "services": {
            "classifier": {
                "vocab_file": "",
                "model_file": ""
            },
            "speech_recog": {
                "vosk": {
                    "model_folder": "./services/speech_recog/vosk_model"
                }
            },
            "synthesizer": {
                "use_ai": False,
                "use_cuda": False,
                "model_file": "",
            },
            "skill_manager": {
                "active_skills": {
                    "datetime": {},
                    "greetings": {}
                }
            }
        }
    }

def config_exists():
    return os.path.exists('config.json')

def save_config(config: dict):
    with open('config.json', 'w') as config_file:
        config_file.write(json.dumps(config, indent=4))

def load_config() -> dict:
    if not os.path.exists('config.json'):
        config = DEFAULT_CONFIG
        save_config(config)
    else:
        config = json.load(open('config.json', 'r'))

    return config