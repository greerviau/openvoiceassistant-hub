import os
import typing
import time

from core import config
from core.schemas import Context
from core.enums import Components
from core.node_manager import NodeManager
from core.skill_manager import SkillManager
from core.integration_manager import IntegrationManager
from core.components.actor import Actor
from core.components.understander import Understander
from core.components.transcriber import Transcriber
from core.components.synthesizer import Synthesizer

COMPONENTS = {
    Components.Transcriber: Transcriber,
    Components.Understander: Understander,
    Components.Actor: Actor,
    Components.Synthesizer: Synthesizer
}

class OpenVoiceAssistant:
    def __init__(self):
        self.base_dir = os.path.realpath(os.path.dirname(__file__))
        self.model_dump = os.path.join(self.base_dir, "model_dump")
        self.file_dump = os.path.join(self.base_dir, "file_dump")
        
        os.makedirs(self.model_dump, exist_ok = True)
        os.makedirs(self.file_dump, exist_ok = True)

        self.restart()  

    def restart(self):
        self.settings = config.get("settings")
        
        timezone = self.settings["timezone"]
        os.environ["TZ"] = timezone
        time.tzset()

        self.load_managers()
        self.launch_all_components()

    def load_managers(self):
        self.node_manager = NodeManager(self)
        self.integration_manager = IntegrationManager(self)
        self.skill_manager = SkillManager(self)

    def component_exists(self, component_id: Components):
        return component_id in self.components

    def get_component(self, component_id: Components):
        if self.component_exists(component_id):
            return self.components[component_id]
        else:
            return None

    def launch_component(self, component_id: Components):
        self.components[component_id] = COMPONENTS[component_id](self)

    def launch_all_components(self):
        self.components = {}
        for component_id in COMPONENTS.keys():
            self.launch_component(component_id)

    def run_pipeline(self, *stages: typing.List[Components], context: Context = None):
        if not context:
            context = {}

        start = time.time()
        
        for stage in stages:
            self.get_component(stage).run_stage(context)

        context['time_to_run_pipeline'] = time.time() - start
