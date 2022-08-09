import wave
import base64
from io import BytesIO

def wave_file_from_b64_encoded(audio_file):
    audio_data = bytes(base64.b64decode(audio_file.encode('utf-8')))
    file_like = BytesIO(audio_data)
    wf = wave.open(file_like, 'rb')
    return wf

def audio_data_to_b64(audio_data):
    audio_base64 = base64.b64encode(audio_data)
    return audio_base64