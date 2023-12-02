from piper.download import ensure_voice_exists, find_voice, get_voices
from piper import PiperVoice

voices_info = get_voices('./piper_voices')
print(voices_info.keys())