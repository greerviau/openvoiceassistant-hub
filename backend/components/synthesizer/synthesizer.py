import importlib
import json
import os
import typing
import time

from backend.enums import Components
from backend import config
from backend.utils.audio import save_wave
from backend.schemas import Context

class Synthesizer:
    def __init__(self, ova: 'OpenVoiceAssistant'):

        self.algo = config.get(Components.Synthesizer.value, 'algorithm').lower().replace(' ', '_')
        self.module = importlib.import_module(f'backend.components.synthesizer.{self.algo}')
        
        self.file_dump = config.get('file_dump')

        if config.get(Components.Synthesizer.value, 'config') is None:
            config.set(Components.Synthesizer.value, 'config', self.module.default_config())

        self.engine = self.module.build_engine()
        os.makedirs(self.file_dump, exist_ok = True)

    def get_algorithm_default_config(self, algorithm_id: str) -> typing.Dict:
        try:
            module = importlib.import_module(f'backend.components.synthesizer.{algorithm_id}')
            return module.default_config()
        except Exception as e:
            print(repr(e))
            raise RuntimeError('Synthesizer algorithm does not exist')
    
    def run_stage(self, context: Context):
        print('Synth Stage')
        response = context['response']
        print('Response: ', response)
        if not response:
            raise RuntimeError('No response to synthesize')

        context['response_audio_file_path'] = os.path.join(self.file_dump, 'response.wav')

        start = time.time()
            
        audio_data, sample_rate, sample_width = self.engine.synthesize(context)

        context['response_audio_data_hex'] = audio_data.hex()
        context['response_audio_sample_rate'] = sample_rate
        context['response_audio_sample_width'] = sample_width

        context['time_to_synthesize'] = time.time() - start
