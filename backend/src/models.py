from pydantic import BaseModel
from typing import Dict

class TranscribeAudio(BaseModel):
    command_audio_data_hex: str = ''
    command_audio_sample_rate: int
    command_audio_sample_width: int
    command_audio_channels: int
    
class RespondAudio(BaseModel):
    node_id: str
    command_audio_data_hex: str = ''
    command_audio_sample_rate: int
    command_audio_sample_width: int
    command_audio_channels: int
    node_callback: str = ''
    hub_callback: str = ''
    last_time_engaged: float
    time_sent: float

class RespondText(BaseModel):
    node_id: str
    command_text: str = ''
    node_callback: str = ''
    hub_callback: str = ''
    last_time_engaged: float
    time_sent: float

class NodeConfig(BaseModel):
    node_id: str
    node_name: str
    node_api_url: str
    mic_index: int
    speaker_index: int
    vad_sensitivity: int
    wakeup: Dict
    recording: Dict
    playback: Dict