from pydantic import BaseModel

class TranscribeAudio(BaseModel):
    command_audio_data_str: str = ''
    command_audio_sample_rate: int
    command_audio_sample_width: int
    command_audio_channels: int
    
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

class NodeConfig(BaseModel):
    node_id: str
    node_name: str
    node_api_url: str
    mic_index: int
    speaker_index: int
    min_audio_sample_length: int
    audio_sample_buffer_length: float
    vad_sensitivity: int