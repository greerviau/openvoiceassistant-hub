from typing import Dict

from backend import config

class Lights:

    def __init__(self, config: Dict, ova: 'OpenVoiceAssistant'):
        self.config = config

    def light_on(self, config: Dict):
        pass

    def light_off(self, config: Dict):
        pass


def build_skill(config: Dict, ova: 'OpenVoiceAssistant'):
    return Lights(config, ova)

def default_config():
    return {}