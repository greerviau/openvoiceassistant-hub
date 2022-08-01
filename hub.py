from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import uvicorn
import wave
from vosk import Model, KaldiRecognizer, SetLogLevel
import json
import wave
import base64
from io import BytesIO
import time
from synthesizer import Synthesizer

SetLogLevel(0)

vosk_model = Model('vosk-model-en-us-0.22')
synth = Synthesizer()

host = '127.0.0.1'
port = 5000
debug = True

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Data(BaseModel):
    audio_file: str
    callback: str
    samplerate: int
    room_id: str
    engaged: bool
    time_sent: float

def log(text, end='\n'):
    if debug:
        print(text, end=end)

@app.get('/is_va_hub')
def is_va_hub(token: str = Depends(oauth2_scheme)):
    return True

@app.post('/understand_from_audio_and_synth')
async def understand_from_audio__data_and_synth(token: str = Depends(oauth2_scheme), data: Data = None):
    if not data:
        raise HTTPException(
                    status_code=404,
                    detail='command invalid',
                    headers={'X-Error': 'There goes my error'})

    audio_file = data.audio_file
    samplerate = data.samplerate
    callback = data.callback
    room_id = data.room_id
    engaged = data.engaged
    time_sent = data.time_sent

    print('Api call delay: ', time.time() - time_sent)

    start_time = time.time()

    audio_data = bytes(base64.b64decode(audio_file.encode('utf-8')))
    file_like = BytesIO(audio_data)
    wf = wave.open(file_like, 'rb')

    print('Time to decode: ', time.time() - start_time)
    start_time = time.time()

    rec = KaldiRecognizer(vosk_model, samplerate)
    rec.SetWords(True)
    res = None
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = rec.Result()
            break
        else:
            _ = rec.PartialResult()    
    if not res:
        res = rec.FinalResult()

    log(f'Final {res}')
    print('Time to transcribe: ', time.time() - start_time)

    if res:
        command = json.loads(res)['text']
        if not command:
            raise HTTPException(
                    status_code=404,
                    detail='command invalid',
                    headers={'X-Error': 'There goes my error'})

        start_time = time.time()

        audio = synth.synthesize_text(command)
        audio_base64 = base64.b64encode(audio)

        print('Time to synthesize: ', time.time() - start_time)
        return {
            'command': command,
            'audio_data': audio_base64,
            'time_sent': time.time()
        }
    else:
        raise HTTPException(
                    status_code=404,
                    detail='invalid audio',
                    headers={'X-Error': 'There goes my error'})

if __name__ == '__main__':
    uvicorn.run(app, host=host, port=port)