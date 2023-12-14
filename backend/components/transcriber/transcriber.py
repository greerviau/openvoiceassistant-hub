import importlib
import os
import typing
import time

from backend.enums import Components
from backend import config
from backend.schemas import Context
from backend.utils.nlp import clean_text

class Transcriber:
    def __init__(self, ova: 'OpenVoiceAssistant'):    
        self.ova = ova

        self.algo = config.get(Components.Transcriber.value, 'algorithm').lower().replace(' ', '_')
        self.module = importlib.import_module(f'backend.components.transcriber.{self.algo}')

        self.verify_config()

        self.engine = self.module.build_engine(ova)

    def verify_config(self):
        current_config = config.get(Components.Transcriber.value, 'config')
        default_config = self.module.default_config()
        try:
            if not current_config or (current_config.keys() != default_config.keys()) or current_config["id"] != default_config["id"]:
                raise Exception("Incorrect config")
        except:
            config.set(Components.Transcriber.value, 'config', default_config)

    def get_algorithm_default_config(self, algorithm_id: str) -> typing.Dict:
        try:
            module = importlib.import_module(f'backend.components.transcriber.{algorithm_id}')
            return module.default_config()
        except Exception as e:
            print(repr(e))
            raise RuntimeError('Transcriber algorithm does not exist')

    def run_stage(self, context: Context):
        print('Transcribing Stage')
        start = time.time()

        command = self.engine.transcribe(context).strip()

        if not command:
            raise RuntimeError('No command')
        
        context['command'] = command
        print(f'Command: {command}')

        cleaned_command = clean_text(command)
        context['cleaned_command'] = cleaned_command
        print(f'Cleaned Command: {cleaned_command}')

        dt = time.time() - start        
        print("Time to transcribe: ", dt)
        context['time_to_transcribe'] = dt
        
