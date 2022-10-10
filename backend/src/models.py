from pydantic import BaseModel

class SkillConfig(BaseModel):
    skill_id: str
    config: dict

class Respond(BaseModel):
    audio_file: str
    text_command: str
    samplerate: int
    callback: str
    node_id: str
    engage: bool
    last_time_engaged: float
    time_sent: float

class NodeInfo(BaseModel):
    ip: str
    port: int
    address: str
    node_id: str