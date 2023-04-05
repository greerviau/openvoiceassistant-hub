from typing import Dict
import pyjokes

from backend import config

class Jokes:

    def __init__(self, config: Dict):
        self.config = config

    def tell_joke(self, config: Dict):
        return pyjokes.get_joke()


def build_skill(config: Dict):
    return Jokes(config)

def default_config():
    return {}