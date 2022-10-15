import importlib
import json
import os
import typing
import time

from backend.config import Configuration
from backend.utils.audio import wave_file_from_audio_data

class Transcriber:
    def __init__(self, config: Configuration):
        self.config = config

        self.algo = self.config.get('components', 'transcriber', 'algorithm')
        self.module = importlib.import_module(f'backend.components.transcriber.{self.algo}')
        
        try:
            self.config.get('components', 'transcriber', 'config')
        except:
            self.config.setkey('components', 'transcriber', 'config', value=self.module.default_config())

        self.engine = self.module.build_engine(self.config)

    def transcribe(self, wave_file, samplerate) -> str:
        return self.engine.transcribe(wave_file, samplerate)

    def run_stage(self, context: typing.Dict):
        print('Transcribing Stage')
        ad_str = context['command_audio_data_str']
        sr = context['command_audio_sample_rate']
        sw = context['command_audio_sample_width']
        c = context['command_audio_channels']

        ad = bytes.fromhex(ad_str)
        
        start = time.time()

        wave_file = wave_file_from_audio_data(
            audio_data=ad, 
            sample_rate=sr, 
            sample_width=sw, 
            channels=c,
            wave_file='command.wav'
        )

        command = self.transcribe(wave_file, sr)
        
        context['time_to_transcribe'] = time.time() - start

        if not command:
            raise RuntimeError('No command to process')
        
        context['command'] = command

        print(f'Command: {command}')
