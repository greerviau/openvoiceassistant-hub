import importlib

class Transcriber:
    def __init__(self, config):
        self.algo = config['services']['transcriber']['alogrithm'].lower()
        self.algo_config = config['services']['transcriber']['config']

        self.module = importlib.import_module(f'.{self.algo}')
        self.engine = self.module.build_engine(self.algo_config)

    def transcribe(self, wave_file, samplerate):
        return self.engine.transcribe(wave_file, samplerate)