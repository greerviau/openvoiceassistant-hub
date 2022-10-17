import importlib
import json
import os
import typing
import time
import wave

from backend.config import Configuration
from backend.schemas import Context
from backend.utils.audio import save_wave

class Transcriber:
    def __init__(self, config: Configuration):
        self.config = config

        self.algo = self.config.get('components', 'transcriber', 'algorithm')
        self.module = importlib.import_module(f'backend.components.transcriber.{self.algo}')

        self.file_dump = self.config.get('file_dump')
        
        try:
            self.config.get('components', 'transcriber', 'config')
        except:
            self.config.setkey('components', 'transcriber', 'config', value=self.module.default_config())

        self.engine = self.module.build_engine(self.config)

    def run_stage(self, context: Context):
        print('Transcribing Stage')
        ad_str = context['command_audio_data_str']
        sr = context['command_audio_sample_rate']
        sw = context['command_audio_sample_width']
        c = context['command_audio_channels']

        ad = bytes.fromhex(ad_str)

        wave_file_path = os.path.join(self.file_dump, 'command.wav')

        save_wave(wave_file_path, ad, sr, sw, c)
        
        start = time.time()

        command = self.engine.transcribe(ad, sr, sw, c, wave_file_path)
        
        context['time_to_transcribe'] = time.time() - start

        if not command:
            raise RuntimeError('No command')
        
        context['command'] = command

        print(f'Command: {command}')
