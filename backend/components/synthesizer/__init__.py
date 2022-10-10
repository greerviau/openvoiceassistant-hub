import importlib
import json
import os
import typing
import time

from backend.utils.audio import audio_data_to_b64
from backend.config import Configuration

class Synthesizer:
    def __init__(self, config: Configuration):
        self.config = config

        self.algo = self.config.get('components', 'synthesizer', 'algorithm').lower()
        self.module = importlib.import_module(f'backend.components.synthesizer.{self.algo}')

        try:
            self.config.get('components', 'synthesizer', 'config')
        except:
            self.config.setkey('components', 'synthesizer', 'config', value=self.module.default_config())

        self.engine = self.module.build_engine(self.config)
        
        self.file_dump = self.config.get('file_dump')
        os.makedirs(self.file_dump, exist_ok = True)
    
    def run_stage(self, context: typing.Dict):
        print('Synth Stage')
        response = context['response']
        print('Response: ', response)
        if not response:
            raise RuntimeError('No response to synthesize')

        start = time.time()
            
        audio_data, sample_rate, sample_width = self.engine.synthesize(response, file_dump=self.file_dump)

        audio_base64 = audio_data_to_b64(audio_data)

        context['time_to_synthesize'] = time.time() - start
        context['audio_data'] = audio_base64
        context['sample_rate'] = sample_rate
        context['sample_width'] = sample_width
