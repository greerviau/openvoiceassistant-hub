import typing

class Context(typing.TypedDict):
    node_id: str
    node_callback: str
    time_sent: float
    engaged: bool
    last_time_engaged: float
    command_audio_data_str: str
    command_audio_data_bytes: bytes
    command_audio_sample_rate: int
    command_audio_sample_width: int
    command_audio_channels: int
    command_audio_file_path: str
    command: str
    cleaned_command: str
    encoded_command: str
    pos_info: typing.Dict
    skill: str
    action: str
    conf: float
    time_to_transcribe: float
    time_to_understand: float
    time_to_action: float
    time_to_synthesize: float
    time_to_run_pipeline: float
    response: str
    response_audio_data_str: str
    response_audio_data_bytes: bytes
    response_audio_sample_rate: str
    response_audio_sample_width: str
    response_audio_file_path: str