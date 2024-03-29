import typing
import time
import os
import uuid
import json
import threading
import asyncio
import logging
logger = logging.getLogger("web")

from fastapi import FastAPI, APIRouter, WebSocket, HTTPException, UploadFile, File, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.openapi.utils import get_openapi

from core import config
from core.dir import FILESDIR, LOGFILE
from core.ova import OpenVoiceAssistant
from core.updater import Updater
from core.enums import Components

class RespondAudio(BaseModel):
    node_id: str = ""
    node_name: str = ""
    node_area: str = ""
    hub_callback: str = ""
    time_sent: float = 0.0
    last_time_engaged: float = 0.0
    command_audio_data: str = ""

class RespondText(BaseModel):
    node_id: str = ""
    node_name: str = ""
    node_area: str = ""
    hub_callback: str = ""
    time_sent: float = 0.0
    last_time_engaged: float = 0.0
    command_text: str = ""

async def log_reader(n=5):
    log_lines = []
    with open(LOGFILE, "r") as file:
        for line in file.readlines()[-n:]:
            if "ERROR" in line:
                log_lines.append(f'<pre><span class="text-red-400">{line}</span></pre>')
            elif "WARNING" in line:
                log_lines.append(f'<pre><span class="text-orange-300">{line}</span></pre>')
            else:
                log_lines.append(f'<pre>{line}</pre>')
        return log_lines

def create_app(ova: OpenVoiceAssistant, updater: Updater):

    app = FastAPI()

    @app.websocket("/ws/log")
    async def logs_websocket(websocket: WebSocket):
        await websocket.accept()

        try:
            while True:
                await asyncio.sleep(1)
                logs = await log_reader(200)
                await websocket.send_text(logs)
        except asyncio.CancelledError:
            logger.warning("WebSocket connection closed")
        except Exception as e:
            logger.error(f"An error occurred in the WebSocket endpoint")
        finally:
            try:
                await websocket.close()
            except Exception as e:
                logger.error(f"An error occurred while closing WebSocket connection")
    
    # SAVE THIS FOR LATER (TODO)
    """@app.websocket("/ws/node/{node_id}/log")
    async def node_logs_websocket(node_id: str, websocket: WebSocket):
        await websocket.accept()
        logger.info("Opened node logs websocket")
        address = ova.node_manager.get_node_config(node_id)["address"]
        try:
            async with socketio.AsyncSimpleClient() as sio:
                await sio.connect(f"http://{address}/ws/log", transports=['websocket'])
                logger.info(f"Socket connection made to {address}")
                while True:
                    logs = await sio.receive()
                    logger.info(logs)
                    await websocket.send_text(logs)
        except asyncio.CancelledError:
            logger.warning("WebSocket connection closed")
        except Exception as e:
            logger.error(f"An error occurred in the WebSocket endpoint: {e}")
        finally:
            try:
                await websocket.close()
            except Exception as e:
                logger.error(f"An error occurred while closing WebSocket connection: {e}")"""

    core = APIRouter(prefix="/api")

    @core.get("", tags=["Core"])
    async def api():
        return {"is_ova": True, "version": updater.version}

    @core.get("/update/available", tags=["Core"])
    async def api():
        try:
            updater.check_for_updates()
            return {
                "update_available": updater.update_available,
                "update_version": updater.update_version,
                "updating": updater.updating
            }
        except:
            raise HTTPException(
                        status_code=400,
                        detail="Failed to check for update",
                        headers={"X-Error": "Failed to check for update"})

    @core.post("/update", tags=["Core"])
    async def api():
        try:
            updater.check_for_updates()
            if updater.update_available:
                threading.Thread(target=updater.update, daemon=True).start()
                return {"success": True}
            else:
                raise HTTPException(
                        status_code=400,
                        detail="No update available",
                        headers={"X-Error": "No update available"})
        except:
            raise HTTPException(
                        status_code=400,
                        detail="Failed to update",
                        headers={"X-Error": "Failed to update"})
    
    @core.get("/config", tags=["Core"])
    async def get_config():
        c = config.get()
        if c:
            return c
        else:
            raise HTTPException(
                        status_code=400,
                        detail="Could not find OVA config",
                        headers={"X-Error": "Could not find OVA config"})
        
    @core.get("/config/default", tags=["Core"])
    async def get_config():
        c = config.DEFAULT_CONFIG
        if c:
            return c
        else:
            raise HTTPException(
                        status_code=400,
                        detail="Could not find OVA default config",
                        headers={"X-Error": "Could not find OVA default config"})            

    @core.put("/config/settings", tags=["Core"])
    async def put_settings(settings: typing.Dict):
        try:
            return config.set("settings", settings)
        except Exception as err:
            raise HTTPException(
                        status_code=400,
                        detail="Failed to set OVA settings",
                        headers={"X-Error": "Failed to set OVA settings"})

    @core.post("/restart", tags=["Core"])
    async def restart():
        if ova:
            ova.restart()
        else:
            raise HTTPException(
                        status_code=400,
                        detail="OVA not initialized",
                        headers={"X-Error": "OVA not initialized"})               

    # TRANSCRIBER

    @core.post("/transcriber/reload", tags=["Transcriber"])
    async def reload_transcriber():
        if ova:
            ova.launch_component(Components.Transcriber)
        else:
            raise HTTPException(
                        status_code=400,
                        detail="Failed to reload Transcriber",
                        headers={"X-Error": "Failed to reload Transcriber"})

    @core.get("/transcriber/config", tags=["Transcriber"])
    async def get_transcriber_config():
        component_config = config.get("transcriber")
        if component_config:
            return component_config
        else:
            raise HTTPException(
                        status_code=400,
                        detail="Could not find transcriber config",
                        headers={"X-Error": "Could not find transcriber config"})
        
    @core.put("/transcriber/config", tags=["Transcriber"])
    async def put_transcriber_config(component_config: typing.Dict):
        try:
            return config.set("transcriber", component_config)
        except Exception as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": "Failed to put transcriber config"})
        
    @core.get("/transcriber/{algorithm_id}/config/default", tags=["Transcriber"])
    async def get_transcriber_default_config(algorithm_id: str):
        try:
            return ova.get_component(Components.Transcriber).get_algorithm_default_config(algorithm_id)
        except Exception as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail="Transcriber algorithm default config does not exist",
                        headers={"X-Error": "Transcriber algorithm default config does not exist"})
        
    # UNDERSTANDER

    @core.post("/understander/reload", tags=["Understander"])
    async def reload_understander():
        if ova:
            ova.launch_component(Components.Understander)
        else:
            raise HTTPException(
                        status_code=400,
                        detail="Failed to reload Understander",
                        headers={"X-Error": "Failed to reload Understander"})

    @core.get("/understander/config", tags=["Understander"])
    async def get_understander_config():
        component_config = config.get("understander")
        if component_config:
            return component_config
        else:
            raise HTTPException(
                        status_code=400,
                        detail="Could not find understander config",
                        headers={"X-Error": "Could not find understander config"})
        
    @core.put("/understander/config", tags=["Understander"])
    async def put_understander_config(component_config: typing.Dict):
        try:
            return config.set("understander", component_config)
        except Exception as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": "Failed to put understander config"})
        
    @core.get("/understander/{algorithm_id}/config/default", tags=["Understander"])
    async def get_understander_default_config(algorithm_id: str):
        try:
            return ova.get_component(Components.Understander).get_algorithm_default_config(algorithm_id)
        except Exception as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail="Transcriber algorithm default config does not exist",
                        headers={"X-Error": "Transcriber algorithm default config does not exist"})
        
    @core.get("/understander/understand/text/{text}", tags=["Understander"])
    async def understand_text(text: str):
        context = {}
        context["command"] = text
        context["time_sent"] = 0.0
        context["last_time_engaged"] = 0.0

        try:
            ova.run_pipeline(Components.Understander, context=context)
        except Exception as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

        return context
    
    # SYNTHESIZER

    @core.post("/synthesizer/reload", tags=["Synthesizer"])
    async def reload_synthesizer():
        if ova:
            ova.launch_component(Components.Synthesizer)
        else:
            raise HTTPException(
                        status_code=400,
                        detail="Failed to reload Synthesizer",
                        headers={"X-Error": "Failed to reload Synthesizer"})

    @core.get("/synthesizer/config", tags=["Synthesizer"])
    async def get_synthesizer_config():
        component_config = config.get("synthesizer")
        if component_config:
            return component_config
        else:
            raise HTTPException(
                        status_code=400,
                        detail="Could not find synthesizer config",
                        headers={"X-Error": "Could not find synthesizer config"})
        
    @core.put("/synthesizer/config", tags=["Synthesizer"])
    async def put_synthesizer_config(component_config: typing.Dict):
        try:
            return config.set("synthesizer", component_config)
        except Exception as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": "Failed to put synthesizer config"})
        
    @core.get("/synthesizer/{algorithm_id}/config/default", tags=["Synthesizer"])
    async def get_synthesizer_default_config(algorithm_id: str):
        try:
            return ova.get_component(Components.Synthesizer).get_algorithm_default_config(algorithm_id)
        except Exception as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail="Synthesizer algorithm default config does not exist",
                        headers={"X-Error": "Synthesizer algorithm default config does not exist"}) 
    
    @core.get("/synthesizer/synthesize/text/{text}", tags=["Synthesizer"])
    async def synthesize_text(text: str):
        context = {}
        context["response"] = text

        try:
            ova.run_pipeline(Components.Synthesizer, context=context)
        except Exception as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

        return context
    
    @core.get("/synthesizer/synthesize/text/{text}/file", tags=["Synthesizer"])
    async def synthesize_text_file(text: str):
        context = {}
        context["response"] = text

        try:
            ova.run_pipeline(Components.Synthesizer, context=context)
        except Exception as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

        response_file_path = context["response_audio_file_path"]
        
        def iterfile():
            with open(response_file_path, mode="rb") as file_like: 
                yield from file_like 

        return StreamingResponse(iterfile(), media_type="audio/wav")

    # NODES

    @core.get("/node/status", tags=["Nodes"])
    async def get_node_status():
        try:
            return ova.node_manager.get_all_node_status()
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.get("/node/{node_id}/status", tags=["Nodes"])
    async def get_node_status(node_id: str):
        try:
            return ova.node_manager.get_node_status(node_id)
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.post("/node/{node_id}/update", tags=["Nodes"])
    async def update_node(node_id: str):
        try:
            return ova.node_manager.update_node(node_id)
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.get("/node/{node_id}/config", tags=["Nodes"])
    async def get_node_config(node_id: str):
        try:
            return ova.node_manager.get_node_config(node_id)
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.put("/node/{node_id}/config", tags=["Nodes"])
    async def put_node_config(node_id: str, node_config: typing.Dict):
        if not node_config:
            raise HTTPException(
                        status_code=400,
                        detail="No config provided",
                        headers={"X-Error": "No config provided"})
        try:
            return ova.node_manager.update_node_config(node_id, node_config)
        except Exception as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.put("/node/{node_id}/sync_up", tags=["Nodes"])
    async def node_sync_up(node_id: str, node_config: typing.Dict):
        if not node_config:
            raise HTTPException(
                        status_code=400,
                        detail="No config provided",
                        headers={"X-Error": "No config provided"})
        try:
            return ova.node_manager.update_node_config(node_id, node_config)
        
        except Exception as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.put("/node/{node_id}/sync_down", tags=["Nodes"])
    async def node_sync_down(node_id: str, node_config: typing.Dict):
        if not node_config:
            raise HTTPException(
                        status_code=400,
                        detail="No config provided",
                        headers={"X-Error": "No config provided"})
        try:
            if not ova.node_manager.node_exists(node_id):
                return ova.node_manager.update_node_config(node_id, node_config)
            else:
                sync_node_config = ova.node_manager.check_for_config_discrepancy(node_id, node_config)
                sync_node_config["restart_required"] = False
                sync_node_config["address"] = node_config["address"]
                sync_node_config["version"] = node_config["version"]
                return ova.node_manager.update_node_config(node_id, sync_node_config)
        
        except Exception as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})
        
    @core.get("/node/{node_id}/hardware", tags=["Nodes"])
    async def get_hardware(node_id: str):
        try:
            return ova.node_manager.get_node_hardware(node_id)
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.get("/node/{node_id}/wake_words", tags=["Nodes"])
    async def get_node_wake_words(node_id: str):
        try:
            return ova.node_manager.get_node_wake_words(node_id)
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})
        
    @core.delete("/node/{node_id}", tags=["Nodes"])
    async def remove_node(node_id: str):
        try:
            return ova.node_manager.remove_node(node_id)
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})
    
    @core.post("/node/{node_id}/restart", tags=["Nodes"])
    async def restart_node(node_id: str):
        try:
            ova.node_manager.restart_node(node_id)
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})
        
    @core.post("/node/{node_id}/announce/{text}", tags=["Nodes"])
    async def node_announce(node_id: str, text: str):
        try:
            context = {}

            node_id = node_id

            context["node_id"] = node_id
            context["response"] = text
            context["synth_response"] = text

            ova.run_pipeline(
                Components.Synthesizer,
                context=context
            )

            data = {
                "audio_data": context["response_audio_data"]
            }
            
            response = ova.node_manager.call_node_api("POST", node_id, "/play/audio", json=data)
            response.raise_for_status()
        
        except Exception as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.post("/node/{node_id}/upload/wake_word_model", tags=["Nodes"])
    async def upload_wake_word_model(node_id: str, wake_word_model: UploadFile = File(...)):
        try:
            files = {"file": (wake_word_model.filename, wake_word_model.file.read(), wake_word_model.content_type)}
            response = ova.node_manager.call_node_api("POST", node_id, "/upload/wake_word_model", files=files)
            response.raise_for_status()
        except Exception as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})   

    @core.get("/node/{node_id}/logs", tags=["Nodes"])
    async def get_logs(node_id: str):
        try:
            resp = ova.node_manager.call_node_api("GET", node_id, "/logs/200")
            resp.raise_for_status()
            return resp.json()
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})          
        
    # SKILLS

    @core.get("/skills/available", tags=["Skills"])
    async def get_available_skills():
        try:
            return sorted(ova.skill_manager.available_skills, key=lambda x: x["name"])
        except RuntimeError as err:
                #logger.info(repr(err))
                raise HTTPException(
                            status_code=400,
                            detail=repr(err),
                            headers={"X-Error": f"{err}"})

    @core.get("/skills/imported", tags=["Skills"])
    async def get_imported_skills():
        try:
            return sorted(ova.skill_manager.imported_skills, key=lambda x: x["name"])
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.get("/skills/not_imported", tags=["Skills"])
    async def get_not_imported_skills():
        try:
            return sorted(ova.skill_manager.not_imported_skills, key=lambda x: x["name"])
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.get("/skills/{skill_id}/config", tags=["Skills"])
    async def get_skill_config(skill_id: str):
        try:
            return ova.skill_manager.get_skill_config(skill_id)
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.get("/skills/{skill_id}/config/default", tags=["Skills"])
    async def get_skill_default_config(skill_id: str):
        try:
            return ova.skill_manager.get_default_skill_config(skill_id)
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.post("/skills/{skill_id}", tags=["Skills"])
    async def post_skill(skill_id: str):
        try:
            return ova.skill_manager.update_skill(skill_id, None)
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.delete("/skills/{skill_id}", tags=["Skills"])
    async def remove_skill(skill_id: str):
        try:
            return ova.skill_manager.remove_skill(skill_id)
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})
                        
    @core.put("/skills/{skill_id}/config", tags=["Skills"])
    async def put_skill_config(skill_id: str, skill_config: typing.Dict):
        try:
            return ova.skill_manager.update_skill(skill_id, skill_config)
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})
        
    # INTEGRATIONS

    @core.get("/integrations/available", tags=["Integrations"])
    async def get_available_integrations():
        try:
            return sorted(ova.integration_manager.available_integrations, key=lambda x: x["name"])
        except RuntimeError as err:
                #logger.info(repr(err))
                raise HTTPException(
                            status_code=400,
                            detail=repr(err),
                            headers={"X-Error": f"{err}"})

    @core.get("/integrations/imported", tags=["Integrations"])
    async def get_imported_integrations():
        try:
            return sorted(ova.integration_manager.imported_integrations, key=lambda x: x["name"])
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.get("/integrations/not_imported", tags=["Integrations"])
    async def get_not_imported_integrations():
        try:
            return sorted(ova.integration_manager.not_imported_integrations, key=lambda x: x["name"])
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.get("/integrations/{integration_id}/config", tags=["Integrations"])
    async def get_integration_config(integration_id: str):
        try:
            return ova.integration_manager.get_integration_config(integration_id)
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.get("/integrations/{integration_id}/config/default", tags=["Integrations"])
    async def get_integration_default_config(integration_id: str):
        try:
            return ova.integration_manager.get_default_integration_config(integration_id)
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.post("/integrations/{integration_id}", tags=["Integrations"])
    async def post_integration(integration_id: str):
        try:
            return ova.integration_manager.update_integration(integration_id, None)
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.delete("/integrations/{integration_id}", tags=["Integrations"])
    async def remove_integration(integration_id: str):
        try:
            return ova.integration_manager.remove_integration(integration_id)
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})
                        
    @core.put("/integrations/{integration_id}/config", tags=["Integrations"])
    async def put_integration_config(integration_id: str, integration_config: typing.Dict):
        try:
            return ova.integration_manager.update_integration(integration_id, integration_config)
        except RuntimeError as err:
            #logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})
        
    # RESPOND

    @core.post("/respond/audio", tags=["Pipeline"])
    async def respond_to_audio(data: RespondAudio):

        context = {}
        try:
            audio_file_path = os.path.join(FILESDIR, f"command_{data.node_id}.wav")

            command_audio_data = bytes.fromhex(data.command_audio_data)
            with open(audio_file_path, "wb") as file:
                file.write(command_audio_data)

            context["command_audio_file_path"] = audio_file_path

            logger.info(f"Request From {data.node_id}")
            logger.info(f"- Node Name:    {data.node_name}")
            logger.info(f"- Node Area:    {data.node_area}")
            logger.info(f"- HUB Callback: {data.hub_callback}")

            context["node_id"] = data.node_id
            context["node_name"] = data.node_name
            context["node_area"] = data.node_area
            context["hub_callback"] = data.hub_callback
            context["time_sent"] = data.time_sent
            context["time_received"] = time.time()
            context["last_time_engaged"] = data.last_time_engaged

            ova.run_pipeline(
                Components.Transcriber,
                Components.Understander,
                Components.Actor,
                Components.Synthesizer,
                context=context
            )

            context["time_returned"] = time.time()

            return context
        
        except Exception as err:
            logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.post("/respond/audio_file", tags=["Pipeline"])
    async def respond_to_audio_file(audio_file: UploadFile = File(...)):

        context = {}
        try:
            audio_file_path = os.path.join(FILESDIR, audio_file.filename)
            with open(audio_file_path, "wb") as file:
                file.write(await audio_file.read())

            context["command_audio_file_path"] = audio_file_path

            logger.info(f"Request From Frontend")

            context["node_id"] = "frontend"
            context["node_name"] = "Frontend"
            context["node_area"] = "frontend"
            context["hub_callback"] = ""
            context["time_sent"] = 0.0
            context["time_received"] = time.time()
            context["last_time_engaged"] = 0.0

            ova.run_pipeline(
                Components.Transcriber,
                Components.Understander,
                Components.Actor,
                Components.Synthesizer,
                context=context
            )

            context["time_returned"] = time.time()

            context.pop("response_audio_data")

            response_file_path = context["response_audio_file_path"]
            with open(response_file_path, "rb") as file:
                wav_data = file.read()

            response_headers = {"Content-Type": "application/json"}
            response_headers["X-JSON-Data"] = json.dumps(context)
            
            return Response(content=wav_data , headers=response_headers, media_type="audio/wav")
        
        except Exception as err:
            logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    @core.post("/respond/text", tags=["Pipeline"])
    async def respond_to_text(data: RespondText):
        
        context = {}
        try:
            logger.info(f"Request From {data.node_id}")
            logger.info(f"- Node Name:    {data.node_name}")
            logger.info(f"- Node Area:    {data.node_area}")
            logger.info(f"- HUB Callback: {data.hub_callback}")
            logger.info(f"- Command:      {data.command_text}")

            context["node_id"] = data.node_id
            context["node_name"] = data.node_name
            context["node_area"] = data.node_area
            context["command"] = data.command_text
            context["hub_callback"] = data.hub_callback
            context["time_sent"] = data.time_sent
            context["time_received"] = time.time()
            context["last_time_engaged"] = data.last_time_engaged

            ova.run_pipeline(
                Components.Understander,
                Components.Actor,
                Components.Synthesizer,
                context=context
            )

            context["time_returned"] = time.time()
            
            context.pop("response_audio_data")

            response_file_path = context["response_audio_file_path"]
            with open(response_file_path, "rb") as file:
                wav_data = file.read()

            response_headers = {"Content-Type": "application/json"}
            response_headers["X-JSON-Data"] = json.dumps(context)
            
            return Response(content=wav_data , headers=response_headers, media_type="audio/wav")
        except Exception as err:
            logger.info(repr(err))
            raise HTTPException(
                        status_code=400,
                        detail=repr(err),
                        headers={"X-Error": str(err)})

    app.include_router(core)

    app.mount("/static", StaticFiles(directory="./frontend/build/static"), name="static")

    templates = Jinja2Templates(directory="./frontend/build")

    @app.get("/{path:path}")
    async def serve_static_files(path: str, request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="Open Voice Assistant HUB",
            version="0.0.1",
            description="API Schema for Open Voice Assistant HUB",
            routes=core.routes,
        )
        openapi_schema["info"]["x-logo"] = {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        }
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    return app