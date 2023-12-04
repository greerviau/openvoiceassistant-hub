import os
import json
import typing

from backend.enums import Components

DEFAULT_CONFIG = {
        "engage_delay": 30,
        "base_dir": os.path.realpath(os.path.dirname(__file__)),
        "model_dump": f"{os.path.realpath(os.path.dirname(__file__))}/model_dump",
        "file_dump": f"{os.path.realpath(os.path.dirname(__file__))}/file_dump",
        Components.Transcriber.value: {
            "algorithm": "Kaldi",
            "algorithm_options": [
                "Kaldi", 
                "Whisper"
            ]
        },
        Components.Understander.value: {
            "algorithm": "Rapidfuzz",
            "algorithm_options": [
                "Rapidfuzz",
                "Neural Intent"
            ]
        },
        Components.Synthesizer.value: {
            "algorithm": "Espeak",
            "algorithm_options": [
                "Espeak",
                "Coqui",
                "Piper"
            ]
        },
        "nodes": {},
        "integrations":{},
        "skills": {
            "default": {}
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

def set(*keys: typing.List[str]):
    global config
    keys = list(keys)
    value = keys.pop(-1)
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
