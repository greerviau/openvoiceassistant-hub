import wave
import base64
from io import BytesIO

def wave_file_from_b64_encoded(audio_file, save=False):
    audio_data = bytes(base64.b64decode(audio_file.encode('utf-8')))

    if not save:
        wave_file = BytesIO()
    else:
        wave_file = 'command.wav'

    wf = wave.open(wave_file, 'wb')
    wf.setnchannels(self.CHANNELS)
    wf.setsampwidth(self.SAMPLEWIDTH)
    wf.setframerate(self.RATE)
    wf.writeframes(audio_data)

    return wf

def audio_data_to_b64(audio_data):
    audio_base64 = base64.b64encode(audio_data)
    return audio_base64