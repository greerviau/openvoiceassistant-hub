import fastapi
from fastapi.encoders import jsonable_encoder

from backend.ova import OpenVoiceAssistant
from backend.src.models import *

def create_app(ova: OpenVoiceAssistant):

    router = fastapi.APIRouter(prefix="/api")

    @router.get('/')
    async def index():
        return {"Success"}

    # SKILLS

    @router.get('/skills/available')
    async def get_available_skills():
        return ova.get_component('skillset').available_skills

    @router.get('/skills/active')
    async def get_active_skills():
        return ova.get_component('skillset').imported_skills

    @router.get('/skills/config/{skill_id}')
    async def get_skill_config(skill_id: str):
        try:
            return ova.get_component('skillset').get_skill_config(skill_id)
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=404,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})


    @router.post('/skills/{skill_id}')
    async def post_skill(skill_id: str):
        try:
            ova.get_component('skillset').add_skill(skill_id)
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=404,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.post('/skills/')
    async def post_skill(data: SkillConfig):
        try:
            ova.get_component('skillset').add_skill_config(data.skill_id, data.config)
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=404,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})
                        
    @router.put('/skills/config/')
    async def put_skill_config(data: SkillConfig):
        try:
            ova.get_component('skillset').update_skill_config(data.skill_id, data.config)
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=404,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    # NODES

    @router.put('/node/sync')
    async def sync(data: NodeInfo = None):
        if not data:
            raise fastapi.HTTPException(
                        status_code=404,
                        detail='command invalid',
                        headers={'X-Error': 'No data provided'})
        try:
            ova.node_manager.update_node_config(data.node_id, jsonable_encoder(data))
        except Exception as err:
            raise fastapi.HTTPException(
                        status_code=404,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.get('/node/status')
    async def get_node_status():
        try:
            return ova.node_manager.get_node_status()
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=404,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.get('/node/status/{node_id}')
    async def get_node_status(node_id: str):
        try:
            return ova.node_manager.get_node_status()
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=404,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.get('/node/config/{node_id}')
    async def get_node_status(node_id: str):
        try:
            return ova.node_manager.get_node_config(node_id)
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=404,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    # RESPOND

    @router.post('/respond/audio')
    async def respond_to_audio(data: RespondToAudio):

        context = {}

        context['audio_file'] = data.audio_file
        context['samplerate'] = int(data.samplerate)
        context['callback'] = data.callback
        context['node_id'] = data.node_id
        context['time_sent'] = float(data.time_sent)
        context['last_time_engaged'] = float(data.last_time_engaged)

        ova.run_pipeline('transcriber','understander', 'skillset', 'synthesizer', context=context)

        return context

    
    app = fastapi.FastAPI()
    app.include_router(router)

    return app