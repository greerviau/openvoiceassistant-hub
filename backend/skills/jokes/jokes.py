import typing
import pyjokes

class Jokes:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova

    def tell_joke(self, context: typing.Dict):
        return pyjokes.get_joke()


def build_skill(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    return Jokes(skill_config, ova)

def default_config():
    return {
        "name": "Jokes"
    }