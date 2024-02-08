import os
import json
import typing

from core.enums import Components
from core.skills import default

DEFAULT_CONFIG = {
        Components.Transcriber.value: {
            "algorithm": "kaldi",
            "algorithm_options": [
                "kaldi", 
                "whisper"
            ]
        },
        Components.Understander.value: {
            "algorithm": "rapid_fuzz",
            "algorithm_options": [
                "rapid_fuzz",
                "neural_intent"
            ]
        },
        Components.Synthesizer.value: {
            "algorithm": "espeak",
            "algorithm_options": [
                "espeak",
                "coqui",
                "piper"
            ]
        },
        "nodes": {},
        "integrations":{},
        "skills": {
            "default": default.default_config()
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

def set(*keys: typing.List[typing.Any]):
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
    #print('Config saved')
    with open(config_path, 'w') as config_file:
        config_file.write(json.dumps(config, indent=4))

def verify_config():
    global config
    if list(DEFAULT_CONFIG.keys()) == list(config.keys()):
        return
    config_clone = config.copy()
    for key, value in DEFAULT_CONFIG.items():
        if key not in config_clone:
            set(key, value)
    for key, value in config.items():
        if key not in DEFAULT_CONFIG:
            config_clone.pop(key)
    config = config_clone
    save_config()

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
        verify_config

load_config()
