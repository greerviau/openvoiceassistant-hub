import time
import importlib

from backend.enums import Components
from backend import config
from backend.utils.nlp import clean_text
from backend.schemas import Context
from backend.utils.nlp import information_extraction, encode_command

class Understander:
    def __init__(self, ova: "OpenVoiceAssistant"):
        self.algo = config.get(Components.Understander.value, "algorithm").lower().replace(" ", "_")
        self.module = importlib.import_module(f"backend.components.understander.{self.algo}")

        if config.get(Components.Understander.value, "config") is None:
            config.set(Components.Understander.value, "config", self.module.default_config())

        self.engage_delay = config.get("engage_delay")

        self.engine = self.module.build_engine()
    
    def run_stage(self, context: Context):
        print("Understanding Stage")

        time_sent = context["time_sent"]
        last_time_engaged = context["last_time_engaged"]

        delta_time = time_sent - last_time_engaged
        
        start = time.time()
        
        command = context["command"]

        context["pos_info"] = information_extraction(command)

        try:
            cleaned_command = context["cleaned_command"]
        except KeyError:
            cleaned_command = clean_text(command)
            context["cleaned_command"] = cleaned_command
            print(f"Cleaned Command: {cleaned_command}")

        encoded_command = encode_command(cleaned_command)
        context["encoded_command"] = encoded_command
        print(f"Encoded command: {encoded_command}")
        
        if encoded_command == "BLANK":
            skill = "DID_NOT_UNDERSTAND"
            action = ""
            conf = 1000
        else:
            hub_callback = context["hub_callback"] if "hub_callback" in context else None
            if hub_callback:
                try:
                    skill, action = hub_callback.split('.')
                    conf = 100
                    context["hub_callback"] = ''
                except:
                    raise RuntimeError("Failed to parse callback")
            else:
                try:
                    skill, action, conf = self.engine.understand(context)
                except RuntimeError:
                    skill = "DID_NOT_UNDERSTAND"
                    action = ''
                    conf = 100

        context["time_to_understand"] = time.time() - start
        context["skill"] = skill
        context["action"] = action
        context["conf"] = conf

