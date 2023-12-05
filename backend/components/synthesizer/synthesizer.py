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
        self.file_dump = config.get('file_dump')
        os.makedirs(self.file_dump, exist_ok = True)

        self.algo = config.get(Components.Synthesizer.value, 'algorithm').lower().replace(' ', '_')
        self.module = importlib.import_module(f'backend.components.synthesizer.{self.algo}')

        self.verify_config()

        self.engine = self.module.build_engine()

    def verify_config(self):
        current_config = config.get(Components.Synthesizer.value, 'config')
        default_config = self.module.default_config()
        if not current_config or (current_config.keys() != default_config.keys()):
            config.set(Components.Synthesizer.value, 'config', default_config)

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
        
        response_file_path = os.path.join(self.file_dump, 'response.wav')
        context['response_audio_file_path'] = response_file_path

        start = time.time()
            
        if not self.engine.synthesize(context):
            raise RuntimeError('Failed to synthesize')

        context['response_audio_data'] = open(response_file_path, 'rb')

        context['time_to_synthesize'] = time.time() - start
