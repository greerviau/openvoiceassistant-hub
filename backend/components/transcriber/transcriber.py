import importlib
import json
import os
import typing
import time
import wave

from backend import config
from backend.schemas import Context
from backend.utils.audio import save_wave
from backend.utils.nlp import clean_text

class Transcriber:
    def __init__(self):
        self.algo = config.get('components', 'transcriber', 'algorithm').lower().replace(' ', '_')
        self.module = importlib.import_module(f'backend.components.transcriber.{self.algo}')

        self.file_dump = config.get('file_dump')

        self.wake_word = config.get('wake_word')
        
        try:
            config.get('components', 'transcriber', 'config')
        except:
            config.set('components', 'transcriber', 'config', self.module.default_config())

        self.engine = self.module.build_engine()

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

        audio_data_str = context['command_audio_data_str']

        context['command_audio_data_bytes'] = bytes.fromhex(audio_data_str)

        context['command_audio_file_path'] = os.path.join(self.file_dump, 'command.wav')

        #save_wave(wave_file_path, audio_data, sample_rate, sample_width, channels)

        command = self.engine.transcribe(context)
        
        context['time_to_transcribe'] = time.time() - start

        if not command:
            raise RuntimeError('No command')
        
        context['command'] = command
        print(f'Command: {command}')

        cleaned_command = clean_text(command)
        context['cleaned_command'] = cleaned_command
        print(f'Cleaned Command: {cleaned_command}')

        engaged = False

        if 'engaged' in context:
            engaged = context['engaged']
            
        context['engaged'] = engaged or self.wake_word in cleaned_command
        
