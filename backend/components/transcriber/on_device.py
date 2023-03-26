import whisper
import numpy as np
import typing
import wave
import os

from backend import config
from backend.schemas import Context

class OnDevice:
    def __init__(self):
        pass

    def transcribe(self, context: Context):
        pass
        
def build_engine():
    return OnDevice()

def default_config():
    return {}