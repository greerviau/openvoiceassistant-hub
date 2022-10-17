import os
import json
import typing

from backend.enums import Components

DEFAULT_CONFIG = {
        "wake_word": "computer",
        "title": "",
        "engage_delay": 30,
        "base_dir": os.path.realpath(os.path.dirname(__file__)),
        "model_dump": f"{os.path.realpath(os.path.dirname(__file__))}/model_dump",
        "file_dump": f"{os.path.realpath(os.path.dirname(__file__))}/file_dump",
        "components": {
            Components.Transcriber.value: {
                "algorithms": ["Vosk", "Whisper", "Wave2Vec"],
                "algorithm": "Vosk"
            },
            Components.Understander.value: {
                "vocab_file": "",
                "model_file": "",
                "conf_thresh": 85
            },
            Components.Skillset.value: {
                "imported_skills": {
                    "greetings": {}
                }
            },
            Components.Synthesizer.value: {
                "algorithms": ["pyttsx", "gradtts"],
                "algorithm": "pyttsx"
            }
        },
        "managers": {
            "node_manager": {
                "nodes": {}
            }
        }
    }

class Configuration:
    def __init__(self):
        self.loc = os.path.realpath(os.path.dirname(__file__))
        self.config_path = f'{self.loc}/config.json'
        print(f'Loading config: {self.config_path}')
        self.config = {}
        self.load_config()

    def get(self, *keys: typing.List[str]):
        dic = self.config.copy()
        for key in keys:
            try:
                dic = dic[key]
            except KeyError:
                return None
        return dic

    def setkey(self, *keys: typing.List[str], value=None):
        if value is None:
            raise RuntimeError
        d = self.config
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value
        self.save_config()
        return value
        
    def config_exists(self):
        return os.path.exists(self.config_path)

    def save_config(self):
        print('Config saved')
        with open(self.config_path, 'w') as config_file:
            config_file.write(json.dumps(self.config, indent=4))

    def load_config(self) -> typing.Dict:  # TODO use TypedDict
        if not os.path.exists(self.config_path):
            print('Loading default config')
            self.config = DEFAULT_CONFIG
            self.save_config()
        else:
            print('Loading existing config')
            self.config = json.load(open(self.config_path, 'r'))