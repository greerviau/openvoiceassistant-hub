from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import uvicorn
import time
import click
import sys
import os
import json
import requests

sys.dont_write_bytecode = True
sys.path.append(os.path.join(os.path.dirname(__file__)))

from data_models import *
from utils.audio_utils import audio_data_to_b64, wave_file_from_b64_encoded
from utils.nlp_utils import clean_text
from speech_recog import SpeechRecog
from classifier import Classifier
from natural_language import NLExtractor
import skill_handler
from synthesizer import Synthesizer

def load_config() -> dict:
    if not os.path.exists('config.json'):
        config = {
            'wake_word': 'computer',
            'title': 'sir',
            'engage_delay': 30,
            'nodes': {}
        }
    else:
        config = json.load(open('config.json', 'r'))

    return config


@click.command()
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=5000)
@click.option('--vosk_model', default='vosk-model')
@click.option('--intent_model', default='intent_model/intent_model.h5')
@click.option('--vocab_file', default='intent_model/vocab.p')
@click.option('--debug', is_flag=True)
def run_hub(host, port, vosk_model, intent_model, vocab_file, debug):

    config = load_config()

    
    TITLE = config['title']
    ENGAGE_DELAY = config['engage_delay']

    recog = SpeechRecog(vosk_model)
    classifier = Classifier(intent_model, vocab_file)
    nl_extractor = NLExtractor()
    synth = Synthesizer()

    app = FastAPI()

    active_skills = json.load(open('active_skills.json', 'r'))

    skill_handler.imports(active_skills)

    #oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    def log(text, end='\n'):
        if debug:
            print(text, end=end)

    @app.get('/ova_api/')
    async def index():
        return {}

    @app.put('/ova_api/sync')
    async def ova_sync(data: NodeInfo = None):
        if not data:
            raise HTTPException(
                        status_code=404,
                        detail='command invalid',
                        headers={'X-Error': 'There goes my error'})

        node_id = data.node_id

        config['nodes'][node_id] = data

        return {}

    @app.get('ova_api/available_skills')
    async def get_available_skills():
        return os.listdir('skills')

    @app.get('ova_api/active_skills')
    async def get_active_skills():
        return active_skills

    @app.put('ova_api/add_skill')
    async def get_add_skill(skill: str):
        active_skills.append(skill)
        with open('active_skills.json', 'w') as file:
            file.write(json.dumps(active_skills, indent=4))
        return {}

    @app.get('ova_api/node_status')
    async def get_node_status():
        node_status = {}
        for node_id, values in config['nodes'].items():
            address = values['address']
            try:
                resp = requests.get(address+'/status')
                if resp.status_code == 200:
                    node_status[node_id] = 'online'
                else:
                    raise
            except:
                node_status[node_id] = 'offline'

        return node_status

    @app.post('/ova_api/respond_to_audio')
    async def respond_to_audio(data: RespondToAudio = None):
        if not data:
            raise HTTPException(
                        status_code=404,
                        detail='command invalid',
                        headers={'X-Error': 'There goes my error'})

        audio_file = data.audio_file
        samplerate = data.samplerate
        callback = data.callback
        node_id = data.node_id
        time_sent = data.time_sent
        last_time_engaged = data.last_time_engaged
        
        context = {}

        wave_file = wave_file_from_b64_encoded(audio_file)
        command = recog.recog_audio(wave_file, samplerate)

        delta_time = time_sent - last_time_engaged

        if command and (TITLE in command or delta_time < ENGAGE_DELAY):
            cleaned_command = clean_text(command)
            context['command'] = command
            context['cleaned_command'] = cleaned_command

            log(f'Command: {cleaned_command}')

            tag, skill, conf = classifier.predict_intent(cleaned_command)
            context['tag'] = tag
            context['skill'] = skill
            context['conf'] = conf

            log(f'Tag: {tag}')
            log(f'Skill: {skill}')
            log(f'Conf: {conf}')

            nl_extractor.extract_from_command(cleaned_command)

            skill_handler.skill_response(context)

            response = context['response']
            log(f'Response: {response}')

            if response:
            
                audio = synth.synthesize_text(' '+response+' ')  # The space ensures the first word will be pronounced
                audio_base64 = audio_data_to_b64(audio)

                context['audio_data'] = audio_base64

                return context
            else:
                raise HTTPException(
                        status_code=404,
                        detail='invalid audio',
                        headers={'X-Error': 'There goes my error'})
        else:
            raise HTTPException(
                        status_code=404,
                        detail='invalid audio',
                        headers={'X-Error': 'There goes my error'})


    uvicorn.run(app, host=host, port=port)

if __name__ == '__main__':
    run_hub()