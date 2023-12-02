import wave
import sys

from piper.download import ensure_voice_exists, find_voice, get_voices
from piper import PiperVoice
from pathlib import Path

voices_info = get_voices('./piper_voices')
print(voices_info.keys())

model = 'en_US-lessac-medium'
data_dir = [str(Path.cwd())]
download_dir = data_dir[0]

ensure_voice_exists(model, data_dir, download_dir, voices_info)
model, config = find_voice('en_US-lessac-medium', data_dir)
voice = PiperVoice.load(model, config_path=config, use_cuda=True)
synthesize_args = {
        "speaker_id": 0,
        "length_scale": 0,
        "noise_scale": 0,
        "noise_w": 0,
        "sentence_silence": 0,
    }

with wave.open('test_file.wav', "wb") as wav_file:
    voice.synthesize("Hello world", wav_file, **synthesize_args)