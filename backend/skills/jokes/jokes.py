from typing import Dict
import pyjokes

from backend import config

class Jokes:

    def __init__(self, config: Dict, ova: 'OpenVoiceAssistant'):
        self.config = config

    def tell_joke(self, config: Dict):
        return pyjokes.get_joke()


def build_skill(config: Dict, ova: 'OpenVoiceAssistant'):
    return Jokes(config, ova)

def default_config():
    return {}