from pydantic import BaseModel

class SkillConfig(BaseModel):
    skill_id: str
    config: dict

class RespondAudio(BaseModel):
    command_audio_data_str: str = ''
    command_audio_sample_rate: int
    command_audio_sample_width: int
    command_audio_channels: int
    node_callback: str
    node_id: str
    engage: bool = False
    last_time_engaged: float
    time_sent: float

class RespondText(BaseModel):
    command_text: str = ''
    node_callback: str
    node_id: str
    engage: bool = False
    last_time_engaged: float
    time_sent: float

class NodeInfo(BaseModel):
    ip: str
    port: int
    address: str
    node_id: str