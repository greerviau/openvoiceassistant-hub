from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import uvicorn
import time
import click
import sys
import os

sys.dont_write_bytecode = True
sys.path.append(os.path.join(os.path.dirname(__file__)))
print(sys.path)

from utils.audio_utils import audio_data_to_b64, wave_file_from_b64_encoded
from utils.nlp_utils import clean_text
from speech_recog import SpeechRecog
from classifier import Classifier
from synthesizer import Synthesizer

@click.command()
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=5000)
@click.option('--vosk_model', default='vosk-model')
@click.option('--intent_model', default='intent_model/intent_model.h5')
@click.option('--vocab_file', default='intent_model/vocab.p')
@click.option('--debug', is_flag=True)
def run_hub(host, port, vosk_model, intent_model, vocab_file, debug):

    recog = SpeechRecog(vosk_model)
    classifier = Classifier(intent_model, vocab_file)
    synth = Synthesizer()

    app = FastAPI()

    #oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    class Data(BaseModel):
        audio_file: str
        callback: str
        samplerate: int
        room_id: str
        engaged: bool

    def log(text, end='\n'):
        if debug:
            print(text, end=end)

    @app.get('/is_alive')
    def is_va_hub():
        return True

    @app.get('/ova_sync')
    def ova_sync():
        return True

    @app.post('/respond_to_audio')
    async def respond_to_audio(data: Data = None):
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

        
        wave_file = wave_file_from_b64_encoded(audio_file)
        command = recog.recog_audio(wave_file, samplerate)
        if command:
            cleaned_command = clean_text(command)
            tag, skill, conf = classifier.predict_intent(cleaned_command)

            log(f'Command {cleaned_command}')
            log(f'Tag: {tag}')
            log(f'Skill: {skill}')
            log(f'Conf: {conf}')
            
            audio = synth.synthesize_text(' '+cleaned_command+' ')  # The space ensures the first word will be pronounced
            audio_base64 = audio_data_to_b64(audio)

            return {
                'command': cleaned_command,
                'audio_data': audio_base64,
                'time_sent': time.time()
            }
        else:
            raise HTTPException(
                        status_code=404,
                        detail='invalid audio',
                        headers={'X-Error': 'There goes my error'})


    uvicorn.run(app, host=host, port=port)

if __name__ == '__main__':
    run_hub()