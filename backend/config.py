import os
import json
import typing

'''
import dataclasses
import dataclasses_json

@dataclasses_json.dataclass_json
@dataclasses.dataclass
class TranscriberConfig:
    algorithms: list[str] = ['vosk', 'wave2vec']
    algorithm: str = 'vosk'
    config: dict = None

@dataclasses_json.dataclass_json
@dataclasses.dataclass
class UnderstanderConfig:
    vocab_file: str
    model_file: str
    conf_thresh: int = 85

@dataclasses_json.dataclass_json
@dataclasses.dataclass
class SkillsetConfig:
    imported_skills: dict[str, dict] = {'greetings': {}}

@dataclasses_json.dataclass_json
@dataclasses.dataclass
class SynthesizerConfig:
    algorithms: list[str] = ['pyttsx', 'gradtts']
    algorithm: str = 'pyttsx'
    config: dict = None

@dataclasses_json.dataclass_json
@dataclasses.dataclass
class Configuration:
    config_path: str
    wake_word: str = 'computer'
    title: str
    engage_delay: str = 30
    save_dir: str
    model_dump: str = '/model_dump'
    components: dict[str, ]

    def save(self, config_path: str = None):
        if config_path is not None:
            self.config_path = config_path

        with open(self.config_path, 'w') as config_file:
            config_file.write(json.dumps(self.to_json(), indent=4))

        print('Config saved')


def load_config(self, config_path: str = None):
    if config_path is None:
        loc = os.path.realpath(os.path.dirname(__file__))
        config_path = f'{loc}/config.json'

    if not os.path.exists(config_path):
        print('Initializing new config')
        config = Configuration(config_path=config_path)
        config.save()
    else:
        print('Loading existing config')
        config = Foo.from_json(json.load(open(config_path, 'r')))

    return config
'''

DEFAULT_CONFIG = {
        "wake_word": "computer",
        "title": "",
        "engage_delay": 30,
        "base_dir": os.path.realpath(os.path.dirname(__file__)),
        "model_dump": f"{os.path.realpath(os.path.dirname(__file__))}/model_dump",
        "file_dump": f"{os.path.realpath(os.path.dirname(__file__))}/file_dump",
        "components": {
            "transcriber": {
                "algorithms": ["vosk", "wave2vec"],
                "algorithm": "vosk"
            },
            "understander": {
                "vocab_file": "",
                "model_file": "",
                "conf_thresh": 85
            },
            "skillset": {
                "imported_skills": {
                    "greetings": {}
                }
            },
            "synthesizer": {
                "algorithms": ["pyttsx", "gradtts"],
                "algorithm": "pyttsx"
            }
        },
        "managers": {
            "component_manager": {
            },
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

    def load_config(self) -> dict:  # TODO use TypedDict
        if not os.path.exists(self.config_path):
            print('Loading default config')
            self.config = DEFAULT_CONFIG
            self.save_config()
        else:
            print('Loading existing config')
            self.config = json.load(open(self.config_path, 'r'))