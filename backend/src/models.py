from pydantic import BaseModel
from typing import Dict

class TranscribeAudio(BaseModel):
    command_audio_data: str
    
class RespondAudio(BaseModel):
    node_id: str
    node_name: str
    node_area: str
    node_callback: str = ''
    hub_callback: str = ''
    time_sent: float
    last_time_engaged: float
    command_audio_data: str

class RespondText(BaseModel):
    node_id: str
    node_name: str
    node_area: str
    node_callback: str = ''
    hub_callback: str = ''
    time_sent: float
    last_time_engaged: float
    command_text: str = ''

class NodeAnnounce(BaseModel):
    node_id: str
    text: str

class NodeConfig(BaseModel):
    node_id: str
    config: dict