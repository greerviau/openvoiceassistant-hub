from typing import Dict

from backend import config

class ShoppingList:

    def __init__(self, config: Dict, ova: 'OpenVoiceAssistant'):
        self.config = config

    def add_to_shopping_list(self, config: Dict):
        pass


def build_skill(config: Dict, ova: 'OpenVoiceAssistant'):
    return ShoppingList(config, ova)

def default_config():
    return {}