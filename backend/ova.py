import asyncio
import os

from backend.config import Configuration
from backend.node_manager import NodeManager

from backend.components.skillset import Skillset
from backend.components.understander import Understander
from backend.components.transcriber import Transcriber
from backend.components.synthesizer import Synthesizer

COMPONENTS = {
    'transcriber': Transcriber,
    'understander': Understander,
    'skillset': Skillset,
    'synthesizer': Synthesizer
}

class OpenVoiceAssistant:
    def __init__(self):
        self.config = Configuration()
        self.node_manager = NodeManager(self.config)
        
        self.launch_all_components()    

    def component_exists(self, component_id: str):
        return component_id in self.components

    def get_component(self, component_id: str):
        if self.component_exists(component_id):
            return self.components[component_id]
        else:
            return None

    def launch_component(self, component_id: str):
        self.components[component_id] = COMPONENTS[component_id](self.config)

    def launch_all_components(self):
        self.components = {}
        for component_id in COMPONENTS.keys():
            self.launch_component(component_id)

    def run_pipeline(self, *stages: list[str], context: dict = None): # TODO better typing
        if context is None:
            context = {}

        for stage in stages:
            self.get_component(stage).run_stage(context)
