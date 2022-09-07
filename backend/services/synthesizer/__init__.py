import importlib
import json
import os

class Synthesizer:
    def __init__(self, config_manager):
        self.algo = config_manager.get('services', 'synthesizer', 'alogrithm').lower()
        try:
            self.algo_config = config_manager.get('services', 'synthesizer', 'config')
        except:
            self.algo_config = json.load(open(f'{os.getcwd()}/{self.algo}/config.json', 'r'))
            config_manager.set('services', 'synthesizer', 'config', value=self.algo_config)

        self.module = importlib.import_module(f'.{self.algo}')
        self.engine = self.module.build_engine(self.algo_config)

    def synthesize(self, text):
        return self.engine.synthesize(text)