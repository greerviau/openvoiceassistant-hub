import importlib

class Synthesizer:
    def __init__(self, config):
        self.algo = config['services']['synthesizer']['alogrithm'].lower()
        self.algo_config = config['services']['synthesizer']['config']

        self.module = importlib.import_module(f'.{self.algo}')
        self.engine = self.module.build_engine(self.algo_config)

    def synthesize(self, text):
        return self.engine.synthesize(text)