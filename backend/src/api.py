from fastapi import APIRouter, HTTPException, Depends
from src.models import *

import os
import json
import requests

from src.models import *
from utils.audio import audio_data_to_b64, wave_file_from_b64_encoded
from utils.nlp import clean_text

from managers.config_manager import ConfigManager
from managers.node_manager import NodeManager
from managers.skill_manager import SkillManager

from services.transcriber import Transcriber
from services.classifier import Classifier
from services.nlp_extractor import NLPExtractor
from services.synthesizer import Synthesizer

config_manager = ConfigManager()
node_manager = NodeManager(config_manager)
skill_manager = SkillManager(config_manager)

transcriber = Transcriber(config_manager)
classifier = Classifier(config_manager)
nl_extractor = NLPExtractor()
synth = Synthesizer(config_manager)

title = config_manager.get('title')
engage_delay = config_manager.get('engage_delay')

router = APIRouter(prefix="/api")

@router.get('/')
async def index():
    return {"Success"}

# SKILLS

@router.put('/skills')
async def put_skill(skill: str):
    if skill_manager.is_skill_imported(skill):
        if skill in os.listdir('skills'):
            skill_config_path = f'skills/{skill}/config.json'
            if os.path.exists(skill_config_path):
                skill_config = json.load(open(skill_config_path))
            else:
                skill_config = {}
            skill_manager.add_skill(skill, skill_config)

            return skill_config
        else:
            raise HTTPException(
                        status_code=404,
                        detail='Skill does not exist',
                        headers={'X-Error': 'There goes my error'})
    else:
        raise HTTPException(
                    status_code=404,
                    detail='Skill does not exist',
                    headers={'X-Error': 'Skill is already imported'})

@router.get('/skills/available')
async def get_available_skills():
    return os.listdir('skills')

@router.get('/skills/active')
async def get_active_skills():
    return skill_manager.list_imported_skills()

@router.get('/skills/config/{skill}')
async def get_skill_config(skill: str):
    if skill_manager.is_skill_imported(skill):
        raise HTTPException(
                    status_code=404,
                    detail='Skill not imported',
                    headers={'X-Error': 'There goes my error'})
    else:
        return skill_manager.get_skill_config(skill)

@router.put('/skills/config/')
async def put_skill_config(skill: str):
    if skill not in skill_manager.imported_skills:
        raise HTTPException(
                    status_code=404,
                    detail='Skill not imported',
                    headers={'X-Error': 'There goes my error'})
    else:
        return skill_manager.get_skill_config(skill)

# NODES

@router.put('/node/sync')
async def sync(data: NodeInfo = None):
    if not data:
        raise HTTPException(
                    status_code=404,
                    detail='command invalid',
                    headers={'X-Error': 'No data provided'})

    node_manager.set_node(data.node_id, data)

    return {"Success"}

@router.get('/node/status')
async def get_node_status():
    node_status = {}
    for node_id, values in node_manager.nodes.items():
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

@router.get('/node/status/{node_id}')
async def get_node_status(node_id: str):
    if node_id in node_manager.nodes:
        return node_manager.get_node_config(node_id)
    else:
        raise HTTPException(
                    status_code=404,
                    detail='Node does not exist',
                    headers={'X-Error': 'There goes my error'})

# RESPOND

@router.post('/respond/audio')
async def respond_to_audio(data: RespondToAudio = None):
    if not data:
        raise HTTPException(
                    status_code=404,
                    detail='No data provided',
                    headers={'X-Error': 'There goes my error'})

    audio_file = data.audio_file
    samplerate = data.samplerate
    callback = data.callback
    node_id = data.node_id
    time_sent = data.time_sent
    last_time_engaged = data.last_time_engaged
    
    context = {}

    wave_file = wave_file_from_b64_encoded(audio_file)
    command = transcriber.transcribe(wave_file, samplerate)

    delta_time = time_sent - last_time_engaged

    if command:
        if title in command or delta_time < engage_delay:
            cleaned_command = clean_text(command)
            context['command'] = command
            context['cleaned_command'] = cleaned_command

            print(f'Command: {cleaned_command}')

            skill, action, conf = classifier.predict_intent(cleaned_command)
            context['skill'] = skill
            context['action'] = action
            context['conf'] = conf

            print(f'Skill: {skill}')
            print(f'Action: {action}')
            print(f'Conf: {conf}')

            nl_extractor.extract_from_command(cleaned_command)

            skill_manager.skill_action(context)

            response = context['response']
            print(f'Response: {response}')

            if response:
            
                audio = synth.synthesize(' '+response+' ')  # The space ensures the first word will be pronounced
                audio_base64 = audio_data_to_b64(audio)

                context['audio_data'] = audio_base64

                return context
            else:
                raise HTTPException(
                        status_code=404,
                        detail='No response',
                        headers={'X-Error': 'There goes my error'})
        else:
            raise HTTPException(
                        status_code=404,
                        detail='Not engaged',
                        headers={'X-Error': 'There goes my error'})
    else:
        raise HTTPException(
                    status_code=404,
                    detail='No command',
                    headers={'X-Error': 'There goes my error'})