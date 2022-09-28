from pydantic import BaseModel

class SkillConfig(BaseModel):
    skill_id: str
    config: dict

class RespondToAudio(BaseModel):
    audio_file: str
    samplerate: int
    callback: str
    node_id: str
    last_time_engaged: str
    time_sent: str

class NodeInfo(BaseModel):
    ip: str
    port: int
    address: str
    node_id: str