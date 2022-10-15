import wave
import base64 
from io import BytesIO

def wave_file_from_audio_data(audio_data, sample_rate: int, sample_width: int, channels: int, wave_file=''):

    if wave_file.split('.')[-1] != 'wav':
        raise RuntimeError('wave_file must have .wav extension')

    if not wave_file:
        wave_file = BytesIO()

    wf = wave.open(wave_file, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sample_width)
    wf.setframerate(sample_rate)
    wf.writeframes(audio_data)

    if isinstance(wave_file, str):
        return wave_file
    return wf

def audio_data_to_b64(audio_data):
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    return audio_base64