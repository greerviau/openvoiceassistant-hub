import wave
import sys
from typing import Any, Dict

from piper.download import ensure_voice_exists, find_voice, get_voices
from piper import PiperVoice
from pathlib import Path

model = 'en_US-lessac-medium'
data_dir = [str(Path.cwd())]
download_dir = data_dir[0]

model_path = Path(model)

voices_info = get_voices('./piper_voices')
#print(voices_info.keys())

ensure_voice_exists(model, data_dir, download_dir, voices_info)
model, config = find_voice('en_US-lessac-medium', data_dir)

voice = PiperVoice.load(model, config_path=config, use_cuda=True)

with wave.open('test_file.wav', "wb") as wav_file:
    voice.synthesize("Hello world", wav_file)