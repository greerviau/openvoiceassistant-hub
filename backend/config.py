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
                "algorithms": ["Vosk", "Whisper"],
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

loc = os.path.realpath(os.path.dirname(__file__))
config_path = f'{loc}/config.json'
config = {}

def get(*keys: typing.List[str]):
    global config
    dic = config.copy()
    for key in keys:
        try:
            dic = dic[key]
        except KeyError:
            return None
    return dic

def set(*keys: typing.List[str], value=None):
    global config
    if value is None:
        raise RuntimeError
    d = config
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = value
    save_config()
    return value
    
def config_exists():
    global config_path
    return os.path.exists(config_path)

def save_config():
    global config, config_path
    print('Config saved')
    with open(config_path, 'w') as config_file:
        config_file.write(json.dumps(config, indent=4))

def load_config() -> typing.Dict:  # TODO use TypedDict
    global config, config_path
    print(f'Loading config: {config_path}')
    if not os.path.exists(config_path):
        print('Loading default config')
        config = DEFAULT_CONFIG
        save_config()
    else:
        print('Loading existing config')
        config = json.load(open(config_path, 'r'))

load_config()
