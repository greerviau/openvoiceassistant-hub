import logging
import typing

import pyjokes

logger = logging.getLogger("skill.pyjokes")


class PyJokes:
    def __init__(self, skill_config: typing.Dict, ova: "OpenVoiceAssistant"):  # noqa: F821
        self.ova = ova

    def tell_joke(self, context: typing.Dict):
        context["response"] = pyjokes.get_joke()
