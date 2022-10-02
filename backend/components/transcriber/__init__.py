import importlib
import json
import os
import typing

from backend.config import Configuration
from backend.utils.audio import wave_file_from_b64_encoded
from backend.utils.nlp import clean_text

class Transcriber:
    def __init__(self, config: Configuration):
        self.config = config

        self.algo = self.config.get('components', 'transcriber', 'algorithm').lower()
        self.module = importlib.import_module(f'backend.components.transcriber.{self.algo}')
        
        try:
            self.config.get('components', 'transcriber', 'config')
        except:
            self.config.setkey('components', 'transcriber', 'config', value=self.module.default_config())

        self.engine = self.module.build_engine(self.config)

    def transcribe(self, wave_file, samplerate):
        return self.engine.transcribe(wave_file, samplerate)

    def run_stage(self, context: typing.Dict):
        af = context['audio_file']
        sr = context['samplerate']
        wave_file = wave_file_from_b64_encoded(af)
        command = self.transcribe(wave_file, sr)

        if not command:
            raise RuntimeError('No command to process')
            
        context['command'] = command
        cleaned_command = clean_text(command)
        context['cleaned_command'] = cleaned_command

        print(f'Command: {cleaned_command}')
