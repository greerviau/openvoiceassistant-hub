import os
import json

DEFAULT_CONFIG = {
        "wake_word": "computer",
        "title": "",
        "engage_delay": 30,
        "services": {
            "classifier": {
                "vocab_file": "",
                "model_file": ""
            },
            "transcriber": {
                "algorithms": ["vosk", "wave2vec"],
                "algorithm": "vosk",
            },
            "synthesizer": {
                "algorithms": ["pyttsx", "gradtts"],
                "algorithm": "gradtts",
            }
        },
        "managers": {
            "skill_manager": {
                "imported_skills": {
                    "greetings": {}
                }
            },
            "node_manager": {
                "nodes": {
                    
                }
            }
        }
    }

class ConfigManager:
    def __init__(self):
        self.loc = os.path.realpath(os.path.dirname(__file__))
        self.config_path = f'{os.getcwd()}/config.json'
        self.config = {}
        self.load_config()

    def get(self, *keys):
        dic = self.config.copy()
        for key in keys:
            dic = dic[key]
        return dic

    def set(self, *keys, value=None):
        if value is None:
            raise RuntimeError
        d = self.config
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value
        self.save_config()
        
    def config_exists(self):
        return os.path.exists(self.config_path)

    def save_config(self):
        with open(self.config_path, 'w') as config_file:
            config_file.write(json.dumps(self.config, indent=4))

    def load_config(self) -> dict:
        if not os.path.exists(self.config_path):
            self.config = DEFAULT_CONFIG
            self.save_config()
        else:
            self.config = json.load(open(self.config_path, 'r'))