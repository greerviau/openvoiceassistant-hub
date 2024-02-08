from TTS.api import TTS

# Running a multi-speaker and multi-lingual model

# Init TTS
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)

# Run TTS

# Text to speech to a file
tts.tts_to_file(text="Hello world!", file_path="output.wav")
