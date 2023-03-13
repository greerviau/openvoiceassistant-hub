import typing
import fastapi
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi

from backend import config
from backend.ova import OpenVoiceAssistant
from backend.src.models import *
from backend.enums import PipelineStages, Components

def create_app(ova: OpenVoiceAssistant):

    router = fastapi.APIRouter(prefix="/api")

    @router.get('')
    async def index():
        return {"Success"}

    # COMPONENTS

    @router.get('/components/{component_id}/config')
    async def get_component_config(component_id: str):
        component_config = config.get('components', component_id)
        if component_config:
            return component_config
        else:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='component does not exist',
                        headers={'X-Error': 'component does not exist'})
        
    @router.get('/components/synthesizer/{algorithm_id}/config/default')
    async def get_synthesizer_default_config(algorithm_id: str):
        try:
            return ova.get_component(Components.Synthesizer).get_algorithm_default_config(algorithm_id)
        except Exception as e:
            print(repr(e))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='Synthesizer algorithm default config does not exist',
                        headers={'X-Error': 'Synthesizer algorithm default config does not exist'})
        
    @router.get('/components/transcriber/{algorithm_id}/config/default')
    async def get_transcriber_default_config(algorithm_id: str):
        try:
            return ova.get_component(Components.Transcriber).get_algorithm_default_config(algorithm_id)
        except Exception as e:
            print(repr(e))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='Transcriber algorithm default config does not exist',
                        headers={'X-Error': 'Transcriber algorithm default config does not exist'})

    # SKILLS

    @router.get('/skills/available')
    async def get_available_skills():
        return ova.get_component(Components.Skillset).available_skills

    @router.get('/skills/active')
    async def get_active_skills():
        return ova.get_component(Components.Skillset).imported_skills

    @router.get('/skills/{skill_id}/config')
    async def get_skill_config(skill_id: str):
        try:
            return ova.get_component(Components.Skillset).get_skill_config(skill_id)
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.get('/skills/{skill_id}/config/default')
    async def get_skill_default_config(skill_id: str):
        try:
            return ova.get_component(Components.Skillset).get_default_skill_config(skill_id)
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.post('/skills/{skill_id}')
    async def post_skill(skill_id: str):
        try:
            ova.get_component(Components.Skillset).add_skill(skill_id)
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.post('/skills/{skill_id}/config')
    async def post_skill_config(skill_id: str, skill_config: typing.Dict):
        try:
            ova.get_component(Components.Skillset).add_skill_config(skill_id, skill_config)
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})
                        
    @router.put('/skills/{skill_id}/config')
    async def put_skill_config(skill_id: str, skill_config: typing.Dict):
        try:
            ova.get_component(Components.Skillset).update_skill_config(skill_id, skill_config)
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    # NODES

    @router.get('/node/status')
    async def get_node_status():
        try:
            return ova.node_manager.get_all_node_status()
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.get('/node/{node_id}/status}')
    async def get_node_status(node_id: str):
        try:
            return ova.node_manager.get_node_status(node_id)
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.get('/node/{node_id}/config')
    async def get_node_config(node_id: str):
        try:
            return ova.node_manager.get_node_config(node_id)
        except RuntimeError as err:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.put('/node/config')
    async def put_node_config(node_config: NodeConfig):
        if not node_config:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='No config provided',
                        headers={'X-Error': 'No config provided'})
        try:
            ova.node_manager.update_node_config(node_config.node_id, jsonable_encoder(node_config))
        except Exception as err:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.put('/node/sync')
    async def node_sync(node_config: NodeConfig):
        if not node_config:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='No config provided',
                        headers={'X-Error': 'No config provided'})
        try:
            if not ova.node_manager.node_exists(node_config.node_id):
                ova.node_manager.add_node_config(node_config.node_id, jsonable_encoder(node_config))

            sync_node_config = ova.node_manager.get_node_config(node_config.node_id)
            sync_node_config["wake_word"] = config.get('wake_word')
            return sync_node_config
        
        except Exception as err:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    # TRANSCRIBE
    @router.post('/transcribe/audio/')
    async def transcribe_audio(data: TranscribeAudio):
        context = {}
        context['command_audio_data_str'] = data.command_audio_data_str
        context['command_audio_sample_rate'] = data.command_audio_sample_rate
        context['command_audio_sample_width'] = data.command_audio_sample_width
        context['command_audio_channels'] = data.command_audio_channels

        ova.run_pipeline(PipelineStages.Transcribe, context=context)

        return context

    # UNDERSTAND
    @router.get('/understand/text/{text}')
    async def understand_text(text: str):
        context = {}
        context['command'] = text
        context['engage'] = True
        context['time_sent'] = 0.0
        context['last_time_engaged'] = 0.0

        ova.run_pipeline(PipelineStages.Understand, context=context)

        return context

    # SYNTHESIZE
    @router.get('/synthesize/text/{text}')
    async def synthesize_text(text: str):
        context = {}
        context['response'] = text

        ova.run_pipeline(PipelineStages.Synthesize, context=context)

        response_file_path = context['response_file_path']

        def iterfile():
            with open(response_file_path, mode="rb") as file_like: 
                yield from file_like 

        return fastapi.responses.StreamingResponse(iterfile(), media_type="audio/wav")

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
        context['engage'] = data.engage
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