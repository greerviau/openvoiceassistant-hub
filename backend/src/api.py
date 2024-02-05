import typing
import time
import os
import fastapi
import uuid
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
        return {"is_ova": True}
    
    @router.get('/config', tags=["Core"])
    async def get_config():
        c = config.get()
        if c:
            return c
        else:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='no config',
                        headers={'X-Error': 'Could not find OVA config'})
        
    @router.get('/config/default', tags=["Core"])
    async def get_config():
        c = config.DEFAULT_CONFIG
        if c:
            return c
        else:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='no config',
                        headers={'X-Error': 'Could not find OVA default config'})

    @router.post('/restart', tags=["Core"])
    async def restart():
        if ova:
            ova.restart()
        else:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='no config',
                        headers={'X-Error': 'OVA not initialized'})               

    # TRANSCRIBER

    @router.post('/transcriber/reload', tags=["Transcriber"])
    async def reload_transcriber():
        if ova:
            ova.launch_component(Components.Transcriber)
        else:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='Failed to reload Transcriber',
                        headers={'X-Error': 'Failed to reload Transcriber'})

    @router.get('/transcriber/config', tags=["Transcriber"])
    async def get_transcriber_config():
        component_config = config.get('transcriber')
        if component_config:
            return component_config
        else:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='Could not find transcriber config',
                        headers={'X-Error': 'Could not find transcriber config'})
        
    @router.put('/transcriber/config', tags=["Transcriber"])
    async def put_transcriber_config(component_config: Dict):
        try:
            config.set('transcriber', component_config)
            return component_config
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': 'Failed to put transcriber config'})
        
    @router.get('/transcriber/{algorithm_id}/config/default', tags=["Transcriber"])
    async def get_transcriber_default_config(algorithm_id: str):
        try:
            return ova.get_component(Components.Transcriber).get_algorithm_default_config(algorithm_id)
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='Transcriber algorithm default config does not exist',
                        headers={'X-Error': 'Transcriber algorithm default config does not exist'})
        
    
    @router.post('/transcriber/transcribe/audio/', tags=["Transcriber"])
    async def transcribe_audio(data: TranscribeAudio):
        context = {}

        file_dump = ova.file_dump

        audio_file_path = os.path.join(file_dump, f"command_{uuid.uuid4().hex}.wav")

        command_audio_data = bytes.fromhex(data.command_audio_data)
        with open(audio_file_path, 'wb') as file:
            file.write(command_audio_data)

        context['command_audio_file_path'] = audio_file_path

        try:
            ova.run_pipeline(Components.Transcriber, context=context)
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

        return context
        
    # UNDERSTANDER

    @router.post('/understander/reload', tags=["Understander"])
    async def reload_understander():
        if ova:
            ova.launch_component(Components.Understander)
        else:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='Failed to reload Understander',
                        headers={'X-Error': 'Failed to reload Understander'})

    @router.get('/understander/config', tags=["Understander"])
    async def get_understander_config():
        component_config = config.get('understander')
        if component_config:
            return component_config
        else:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='Could not find understander config',
                        headers={'X-Error': 'Could not find understander config'})
        
    @router.put('/understander/config', tags=["Understander"])
    async def put_understander_config(component_config: Dict):
        try:
            config.set('understander', component_config)
            return component_config
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': 'Failed to put understander config'})
        
    @router.get('/understander/{algorithm_id}/config/default', tags=["Understander"])
    async def get_understander_default_config(algorithm_id: str):
        try:
            return ova.get_component(Components.Understander).get_algorithm_default_config(algorithm_id)
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='Transcriber algorithm default config does not exist',
                        headers={'X-Error': 'Transcriber algorithm default config does not exist'})
        
    @router.get('/understander/understand/text/{text}', tags=["Understander"])
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
    
    # SYNTHESIZER

    @router.post('/synthesizer/reload', tags=["Synthesizer"])
    async def reload_synthesizer():
        if ova:
            ova.launch_component(Components.Synthesizer)
        else:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='Failed to reload Synthesizer',
                        headers={'X-Error': 'Failed to reload Synthesizer'})

    @router.get('/synthesizer/config', tags=["Synthesizer"])
    async def get_synthesizer_config():
        component_config = config.get('synthesizer')
        if component_config:
            return component_config
        else:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='Could not find synthesizer config',
                        headers={'X-Error': 'Could not find synthesizer config'})
        
    @router.put('/synthesizer/config', tags=["Synthesizer"])
    async def put_synthesizer_config(component_config: Dict):
        try:
            config.set('synthesizer', component_config)
            return component_config
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': 'Failed to put synthesizer config'})
        
    @router.get('/synthesizer/{algorithm_id}/config/default', tags=["Synthesizer"])
    async def get_synthesizer_default_config(algorithm_id: str):
        try:
            return ova.get_component(Components.Synthesizer).get_algorithm_default_config(algorithm_id)
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='Synthesizer algorithm default config does not exist',
                        headers={'X-Error': 'Synthesizer algorithm default config does not exist'}) 
    
    @router.get('/synthesizer/synthesize/text/{text}', tags=["Synthesizer"])
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

        return context
    
    @router.get('/synthesizer/synthesize/text/{text}/file', tags=["Synthesizer"])
    async def synthesize_text_file(text: str):
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

    @router.put('/node/{node_id}/config', tags=["Nodes"])
    async def put_node_config(node_id: str, node_config: dict):
        if not node_config:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='No config provided',
                        headers={'X-Error': 'No config provided'})
        try:
            return ova.node_manager.update_node_config(node_id, jsonable_encoder(node_config))
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.put('/node/{node_id}/sync_up', tags=["Nodes"])
    async def node_sync_up(node_id: str, node_config: dict):
        if not node_config:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='No config provided',
                        headers={'X-Error': 'No config provided'})
        try:
            return ova.node_manager.update_node_config(node_id, jsonable_encoder(node_config))
        
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.put('/node/{node_id}/sync_down', tags=["Nodes"])
    async def node_sync_down(node_id: str, node_config: dict):
        if not node_config:
            raise fastapi.HTTPException(
                        status_code=400,
                        detail='No config provided',
                        headers={'X-Error': 'No config provided'})
        try:
            if not ova.node_manager.node_exists(node_id):
                return ova.node_manager.update_node_config(node_id, jsonable_encoder(node_config))
            else:
                sync_node_config = ova.node_manager.get_node_config(node_id)
                sync_node_config["restart_required"] = False
                return ova.node_manager.update_node_config(node_id, sync_node_config)
        
        except Exception as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})
        
    @router.get('/node/{node_id}/hardware', tags=["Nodes"])
    async def get_hardware(node_id: str):
        try:
            return ova.node_manager.get_node_hardware(node_id)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.get('/node/{node_id}/wake_words', tags=["Nodes"])
    async def get_node_wake_words(node_id: str):
        try:
            return ova.node_manager.get_node_wake_words(node_id)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})
        
    @router.delete('/node/{node_id}', tags=["Nodes"])
    async def remove_node(node_id: str):
        try:
            return ova.node_manager.remove_node(node_id)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})
    
    @router.post('/node/{node_id}/restart', tags=["Nodes"])
    async def restart_node(node_id: str):
        try:
            ova.node_manager.restart_node(node_id)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})
        
    @router.post('/node/{node_id}/announce/{text}', tags=["Nodes"])
    async def node_announce(node_id: str, text: str):
        try:
            context = {}

            node_id = node_id

            context['node_id'] = node_id
            context['response'] = text

            ova.run_pipeline(
                Components.Synthesizer,
                context=context
            )

            data = {
                "audio_data": context['response_audio_data']
            }
            
            ova.node_manager.call_node_api('POST', node_id, f'/play/audio', data=data)

            return {}
        
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

    @router.get('/skills/imported', tags=["Skills"])
    async def get_imported_skills():
        try:
            return ova.skill_manager.imported_skills
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.get('/skills/not_imported', tags=["Skills"])
    async def get_not_imported_skills():
        try:
            return ova.skill_manager.not_imported
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
            return ova.skill_manager.update_skill_config(skill_id, None)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.delete('/skills/{skill_id}', tags=["Skills"])
    async def remove_skill(skill_id: str):
        try:
            return ova.skill_manager.remove_skill(skill_id)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})
                        
    @router.put('/skills/{skill_id}/config', tags=["Skills"])
    async def put_skill_config(skill_id: str, skill_config: typing.Dict):
        try:
            return ova.skill_manager.update_skill_config(skill_id, skill_config)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})
        
    # INTEGRATIONS

    @router.get('/integrations/available', tags=["Integrations"])
    async def get_available_integrations():
        try:
            return ova.integration_manager.available_integrations
        except RuntimeError as err:
                print(repr(err))
                raise fastapi.HTTPException(
                            status_code=400,
                            detail=repr(err),
                            headers={'X-Error': f'{err}'})

    @router.get('/integrations/imported', tags=["Integrations"])
    async def get_imported_integrations():
        try:
            return ova.integration_manager.imported_integrations
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.get('/integrations/not_imported', tags=["Integrations"])
    async def get_not_imported_integrations():
        try:
            return ova.integration_manager.not_imported
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.get('/integrations/{integration_id}/config', tags=["Integrations"])
    async def get_integration_config(integration_id: str):
        try:
            return ova.integration_manager.get_integration_config(integration_id)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.get('/integrations/{integration_id}/config/default', tags=["Integrations"])
    async def get_integration_default_config(integration_id: str):
        try:
            return ova.integration_manager.get_default_integration_config(integration_id)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.post('/integrations/{integration_id}', tags=["Integrations"])
    async def post_integration(integration_id: str):
        try:
            return ova.integration_manager.update_integration_config(integration_id, None)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})

    @router.delete('/integrations/{integration_id}', tags=["Integrations"])
    async def remove_integration(integration_id: str):
        try:
            return ova.integration_manager.remove_integration(integration_id)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})
                        
    @router.put('/integrations/{integration_id}/config', tags=["Integrations"])
    async def put_integration_config(integration_id: str, integration_config: typing.Dict):
        try:
            return ova.integration_manager.update_integration_config(integration_id, integration_config)
        except RuntimeError as err:
            print(repr(err))
            raise fastapi.HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={'X-Error': f'{err}'})
        
    # RESPOND

    @router.post('/respond/audio', tags=["Pipeline"])
    async def respond_to_audio(data: RespondAudio):
        try:
            context = {}

            file_dump = ova.file_dump

            audio_file_path = os.path.join(file_dump, f"command_{data.node_id}.wav")

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

    @router.post('/respond/text', tags=["Pipeline"])
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