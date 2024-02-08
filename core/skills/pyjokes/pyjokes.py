import typing
import pyjokes

class PyJokes:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova

    def tell_joke(self, context: typing.Dict):
        context['response'] = pyjokes.get_joke()


def build_skill(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    return PyJokes(skill_config, ova)

def default_config():
    return {}