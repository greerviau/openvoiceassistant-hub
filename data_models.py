from pydantic import BaseModel

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