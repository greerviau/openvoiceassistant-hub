import fastapi
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi

from backend.ova import OpenVoiceAssistant
from backend.src.models import *
from backend.enums import PipelineStages

def create_app(ova: OpenVoiceAssistant):

    router = fastapi.APIRouter(prefix="/api")

    @router.get('/')
    async def index():
        return {"Success"}

    # SKILLS

    @router.get('/skills/available')
    async def get_available_skills():
        return ova.get_component(PipelineStages.Skillset).available_skills

    @router.get('/skills/active')
    async def get_active_skills():
        return ova.get_component(PipelineStages.Skillset).imported_skills

    @router.get('/skills/config/{skill_id}')
    async def get_skill_config(skill_id: str):
        try:
            return ova.get_component(PipelineStages.Skillset).get_skill_config(skill_id)
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=404,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.get('/skills/default_config/{skill_id}')
    async def get_skill_config(skill_id: str):
        try:
            return ova.get_component(PipelineStages.Skillset).get_skill_config(skill_id)
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=404,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.post('/skills/{skill_id}')
    async def post_skill(skill_id: str):
        try:
            ova.get_component(PipelineStages.Skillset).add_skill(skill_id)
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=404,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.post('/skills/')
    async def post_skill(data: SkillConfig):
        try:
            ova.get_component(PipelineStages.Skillset).add_skill_config(data.skill_id, data.config)
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=404,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})
                        
    @router.put('/skills/config/')
    async def put_skill_config(data: SkillConfig):
        try:
            ova.get_component(PipelineStages.Skillset).update_skill_config(data.skill_id, data.config)
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
            return ova.node_manager.get_all_node_status()
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

    # SYNTHESIZE
    @router.get('/synthesize/text/{text}')
    async def respond_to_text(text: str):
        context = {}
        context['response'] = text

        ova.run_pipeline(PipelineStages.Synthesize, context=context)

        return context

    # RESPOND

    @router.post('/respond/audio')
    async def respond_to_audio(data: RespondAudio):

        context = {}

        context['command_audio_data_str'] = data.command_audio_data_str
        context['command_audio_sample_rate'] = data.command_audio_sample_rate
        context['command_audio_sample_width'] = data.command_audio_sample_width
        context['command_audio_channels'] = data.command_audio_channels
        context['node_callback'] = data.node_callback
        context['node_id'] = data.node_id
        context['engage'] = False
        context['time_sent'] = data.time_sent
        context['last_time_engaged'] = data.last_time_engaged

        ova.run_pipeline(
            PipelineStages.Transcribe,
            PipelineStages.Understand,
            PipelineStages.Skillset,
            PipelineStages.Synthesize,
            context=context
        )

        return context

    @router.post('/respond/text')
    async def respond_to_text(data: RespondText):

        context = {}

        context['command'] = data.command_text
        context['node_callback'] = data.node_callback
        context['node_id'] = data.node_id
        context['engage'] = data.engage
        context['time_sent'] = data.time_sent
        context['last_time_engaged'] = data.last_time_engaged

        ova.run_pipeline(
            PipelineStages.Understand,
            PipelineStages.Skillset,
            PipelineStages.Synthesize,
            context=context
        )

        return context

    app = fastapi.FastAPI()

    app.include_router(router)

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="Open Voice Assistant HUB",
            version="0.0.1",
            description="API Schema for Open Voice Assistant HUB",
            routes=app.routes,
        )
        openapi_schema["info"]["x-logo"] = {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        }
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    return app