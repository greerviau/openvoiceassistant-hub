import importlib
import json
import os

class Transcriber:
    def __init__(self, config_manager):
        self.algo = config_manager.get('services', 'transcriber', 'alogrithm').lower()
        
        try:
            self.algo_config = config_manager.get('services', 'transcriber', 'config')
        except:
            self.algo_config = json.load(open(f'{os.getcwd()}/{self.algo}/config.json', 'r'))
            config_manager.set('services', 'transcriber', 'config', value=self.algo_config)

        self.module = importlib.import_module(f'.{self.algo}')
        self.engine = self.module.build_engine(self.algo_config)

    def transcribe(self, wave_file, samplerate):
        return self.engine.transcribe(wave_file, samplerate)