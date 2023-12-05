import typing
import time
import os
import fastapi
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi

from backend import config
from backend.ova import OpenVoiceAssistant
from backend.src.models import *
from backend.enums import Components

def create_app(ova: OpenVoiceAssistant):

    router = fastapi.APIRouter(prefix="/api")

    @router.get('')
    async def index():
        return {"Success"}
    
    @router.get('/config', tags=["Config"])
    async def get_config():
        c = config.get()
        if c:
            return c
        else:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='no config',
                        headers={'X-Error': 'component does not exist'})

    # COMPONENTS

    @router.get('/components/{component_id}/config', tags=["Components"])
    async def get_component_config(component_id: str):
        component_config = config.get('components', component_id)
        if component_config:
            return component_config
        else:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='component does not exist',
                        headers={'X-Error': 'component does not exist'})
        
    @router.put('/components/{component_id}/config', tags=["Components"])
    async def put_component_config(component_id: str, component_config: Dict):
        try:
            config.set('components', component_id, 'config', component_config)
            return component_config
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(e),
                        headers={'X-Error': 'failed to put config'})
        
    @router.get('/components/synthesizer/{algorithm_id}/config/default', tags=["Components"])
    async def get_synthesizer_default_config(algorithm_id: str):
        try:
            return ova.get_component(Components.Synthesizer).get_algorithm_default_config(algorithm_id)
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='Synthesizer algorithm default config does not exist',
                        headers={'X-Error': 'Synthesizer algorithm default config does not exist'})
        
    @router.get('/components/transcriber/{algorithm_id}/config/default', tags=["Components"])
    async def get_transcriber_default_config(algorithm_id: str):
        try:
            return ova.get_component(Components.Transcriber).get_algorithm_default_config(algorithm_id)
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='Transcriber algorithm default config does not exist',
                        headers={'X-Error': 'Transcriber algorithm default config does not exist'})

    # NODES

    @router.get('/node/status', tags=["Nodes"])
    async def get_node_status():
        try:
            return ova.node_manager.get_all_node_status()
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.get('/node/{node_id}/status', tags=["Nodes"])
    async def get_node_status(node_id: str):
        try:
            return ova.node_manager.get_node_status(node_id)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.get('/node/{node_id}/config', tags=["Nodes"])
    async def get_node_config(node_id: str):
        try:
            return ova.node_manager.get_node_config(node_id)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.put('/node/config', tags=["Nodes"])
    async def put_node_config(node_config: NodeConfig):
        if not node_config:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='No config provided',
                        headers={'X-Error': 'No config provided'})
        try:
            ova.node_manager.update_node_config(node_config.node_id, jsonable_encoder(node_config))
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.put('/node/sync_up', tags=["Nodes"])
    async def node_sync_up(node_config: NodeConfig):
        if not node_config:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='No config provided',
                        headers={'X-Error': 'No config provided'})
        try:
            if ova.node_manager.node_exists(node_config.node_id):
                ova.node_manager.update_node_config(node_config.node_id, jsonable_encoder(node_config))
            else:
                ova.node_manager.add_node_config(node_config.node_id, jsonable_encoder(node_config))
            sync_node_config = ova.node_manager.get_node_config(node_config.node_id)
            return sync_node_config
        
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.put('/node/sync_down', tags=["Nodes"])
    async def node_sync_down(node_config: NodeConfig):
        if not node_config:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='No config provided',
                        headers={'X-Error': 'No config provided'})
        try:
            if not ova.node_manager.node_exists(node_config.node_id):
                ova.node_manager.add_node_config(node_config.node_id, jsonable_encoder(node_config))
            sync_node_config = ova.node_manager.get_node_config(node_config.node_id)
            return sync_node_config
        
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})
        
    @router.post('/node/say', tags=["Nodes"])
    async def node_say(data: NodeSay):
        try:
            context = {}

            node_id = data.node_id

            context['node_id'] = data.node_id
            context['response'] = data.text

            ova.run_pipeline(
                Components.Synthesizer,
                context=context
            )
            
            ova.node_manager.call_node_api('PUT', node_id, '/say', context)
        
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})
        
    # SKILLS

    @router.get('/skills/available', tags=["Skills"])
    async def get_available_skills():
        try:
            return ova.skill_manager.available_skills
        except RuntimeError as err:
                print(repr(err))
                raise fastapi.HTTPException(
                            status_code=400,
                            detail=repr(err),
                            headers={'X-Error': f'{err}'})

    @router.get('/skills/active', tags=["Skills"])
    async def get_active_skills():
        try:
            return ova.skill_manager.imported_skills
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.get('/skills/{skill_id}/config', tags=["Skills"])
    async def get_skill_config(skill_id: str):
        try:
            return ova.skill_manager.get_skill_config(skill_id)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.get('/skills/{skill_id}/config/default', tags=["Skills"])
    async def get_skill_default_config(skill_id: str):
        try:
            return ova.skill_manager.get_default_skill_config(skill_id)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.post('/skills/{skill_id}', tags=["Skills"])
    async def post_skill(skill_id: str):
        try:
            ova.skill_manager.add_skill(skill_id)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.post('/skills/{skill_id}/config', tags=["Skills"])
    async def post_skill_config(skill_id: str, skill_config: typing.Dict):
        try:
            ova.skill_manager.add_skill_config(skill_id, skill_config)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})
                        
    @router.put('/skills/{skill_id}/config', tags=["Skills"])
    async def put_skill_config(skill_id: str, skill_config: typing.Dict):
        try:
            ova.skill_manager.update_skill_config(skill_id, skill_config)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})
        
    # INTEGRATIONS

    @router.get('/integrations/available', tags=["Integration"])
    async def get_available_integrations():
        try:
            return ova.integration_manager.available_integrations
        except RuntimeError as err:
                print(repr(err))
                raise fastapi.HTTPException(
                            status_code=400,
                            detail=repr(err),
                            headers={'X-Error': f'{err}'})

    @router.get('/integrations/active', tags=["Integration"])
    async def get_active_integrations():
        try:
            return ova.integration_manager.imported_integrations
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.get('/integrations/{integration_id}/config', tags=["Integration"])
    async def get_integration_config(integration_id: str):
        try:
            return ova.integration_manager.get_integration_config(integration_id)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.get('/integrations/{integration_id}/config/default', tags=["Integration"])
    async def get_integration_default_config(integration_id: str):
        try:
            return ova.integration_manager.get_default_integration_config(integration_id)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.post('/integrations/{integration_id}', tags=["Integration"])
    async def post_integration(integration_id: str):
        try:
            ova.integration_manager.add_integration(integration_id)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.post('/integrations/{integration_id}/config', tags=["Integration"])
    async def post_integration_config(integration_id: str, integration_config: typing.Dict):
        try:
            ova.integration_manager.add_integration_config(integration_id, integration_config)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})
                        
    @router.put('/integrations/{integration_id}/config', tags=["Integration"])
    async def put_integration_config(integration_id: str, integration_config: typing.Dict):
        try:
            ova.integration_manager.update_integration_config(integration_id, integration_config)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    # TRANSCRIBE

    @router.post('/transcribe/audio/', tags=["Inference"])
    async def transcribe_audio(data: TranscribeAudio):
        context = {}
        context['command_audio_data_hex'] = data.command_audio_data_hex
        context['command_audio_sample_rate'] = data.command_audio_sample_rate
        context['command_audio_sample_width'] = data.command_audio_sample_width
        context['command_audio_channels'] = data.command_audio_channels

        try:
            ova.run_pipeline(Components.Transcriber, context=context)
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

        return context

    # UNDERSTAND

    @router.get('/understand/text/{text}', tags=["Inference"])
    async def understand_text(text: str):
        context = {}
        context['command'] = text
        context['time_sent'] = 0.0
        context['last_time_engaged'] = 0.0

        try:
            ova.run_pipeline(Components.Understander, context=context)
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

        return context

    # SYNTHESIZE

    @router.get('/synthesize/text/{text}', tags=["Inference"])
    async def synthesize_text(text: str):
        context = {}
        context['response'] = text

        try:
            ova.run_pipeline(Components.Synthesizer, context=context)
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

        response_file_path = context['response_file_path']

        def iterfile():
            with open(response_file_path, mode="rb") as file_like: 
                yield from file_like 

        return fastapi.responses.StreamingResponse(iterfile(), media_type="audio/wav")

    # RESPOND

    @router.post('/respond/audio', tags=["Inference"])
    async def respond_to_audio(data: RespondAudio):
        try:
            context = {}

            file_dump = config.get('file_dump')

            audio_file_path = os.path.join(file_dump, 'command.wav')

            command_audio_data = bytes.fromhex(data.command_audio_data)
            with open(audio_file_path, 'wb') as file:
                file.write(command_audio_data)

            context['command_audio_file_path'] = audio_file_path

            context['node_id'] = data.node_id
            context['node_name'] = data.node_name
            context['node_area'] = data.node_area
            context['node_callback'] = data.node_callback
            context['hub_callback'] = data.hub_callback
            context['time_sent'] = data.time_sent
            context['time_recieved'] = time.time()
            context['last_time_engaged'] = data.last_time_engaged

            ova.run_pipeline(
                Components.Transcriber,
                Components.Understander,
                Components.Actor,
                Components.Synthesizer,
                context=context
            )

            context['time_returned'] = time.time()

            return context
        
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.post('/respond/text', tags=["Inference"])
    async def respond_to_text(data: RespondText):
        try:
            context = {}

            context['node_id'] = data.node_id
            context['command'] = data.command_text
            context['node_callback'] = data.node_callback
            context['hub_callback'] = data.hub_callback
            context['time_sent'] = data.time_sent
            context['time_recieved'] = time.time()
            context['last_time_engaged'] = data.last_time_engaged

            ova.run_pipeline(
                Components.Understander,
                Components.Actor,
                Components.Synthesizer,
                context=context
            )

            context['time_returned'] = time.time()
            
            return context
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

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