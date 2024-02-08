import typing
from mathparse import mathparse

from core.utils.nlp import remove_words

class Mathparse:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova

    def equation(self, context: typing.Dict):
        command = context["cleaned_command"]

        try:
            math_command = remove_words(
                command,
                ['whats', 'what', 'is', 'the']
            )

            res = mathparse.parse(math_command, language='ENG')

            response = math_command + f" is {round(res, 2)}"

            context['response'] = response

        except Exception as e:
            context['response'] = "I couldn't perform that math equation"

def build_skill(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    return Mathparse(skill_config, ova)

def default_config():
    return {}