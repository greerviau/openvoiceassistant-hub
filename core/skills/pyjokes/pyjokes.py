import typing
import pyjokes
import logging
logger = logging.getLogger("skill.pyjokes")

class PyJokes:

    def __init__(self, skill_config: typing.Dict, ova: "OpenVoiceAssistant"):
        self.ova = ova

    def tell_joke(self, context: typing.Dict):
        context["response"] = pyjokes.get_joke()