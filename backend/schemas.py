import typing

class Context(typing.TypedDict):
    command_audio_data_str: str
    command_audio_sample_rate: int
    command_audio_sample_width: int
    command_audio_channels: int
    command: str
    cleaned_command: str
    node_callback: str
    node_id: str
    engage: bool
    time_sent: float
    last_time_engaged: float
    time_to_run_pipeline: float
    time_to_transcribe: float
    time_to_synthesize: float
    time_to_understand: float
    response: str
    response_audio_data_str: str
    response_sample_rate: str
    response_sample_width: str
    skill: str
    action: str
    conf: float