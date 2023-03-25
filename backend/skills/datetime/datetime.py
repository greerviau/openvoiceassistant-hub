from typing import Dict

class Datetime:
    def __init__(self, config: Dict):
        self.config = config

def build_skill(config: Dict):
    return Datetime(config)

def default_config():
    return {}