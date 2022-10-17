import importlib
import json
import os
import typing
import time

from backend.utils.audio import save_wave
from backend.config import Configuration
from backend.schemas import Context

class Synthesizer:
    def __init__(self, config: Configuration):
        self.config = config

        self.algo = self.config.get('components', 'synthesizer', 'algorithm').lower()
        self.module = importlib.import_module(f'backend.components.synthesizer.{self.algo}')
        
        self.file_dump = self.config.get('file_dump')

        try:
            self.config.get('components', 'synthesizer', 'config')
        except:
            self.config.setkey('components', 'synthesizer', 'config', value=self.module.default_config())

        self.engine = self.module.build_engine(self.config)
        os.makedirs(self.file_dump, exist_ok = True)
    
    def run_stage(self, context: Context):
        print('Synth Stage')
        response = context['response']
        print('Response: ', response)
        if not response:
            raise RuntimeError('No response to synthesize')

        file_path = os.path.join(self.file_dump, 'response.wav')

        start = time.time()
            
        audio_data, sample_rate, sample_width = self.engine.synthesize(response, file_path)

        save_wave(
            file_path,
            audio_data=audio_data, 
            sample_rate=sample_rate,
            sample_width=sample_width, 
            channels=1
        )

        audio_str = audio_data.hex()

        context['time_to_synthesize'] = time.time() - start
        context['response_audio_data_str'] = audio_str
        context['response_sample_rate'] = sample_rate
        context['response_sample_width'] = sample_width
