from pydantic import BaseModel

class TranscribeAudio(BaseModel):
    command_audio_data: str
    
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