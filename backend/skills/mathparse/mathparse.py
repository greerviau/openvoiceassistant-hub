from typing import Dict, List
from mathparse import mathparse

from backend import config

class Mathparse:

    def __init__(self, config: Dict, ova: 'OpenVoiceAssistant'):
        self.config = config

    def equation(self, config: Dict):
        command = config["cleaned_command"]

        math_command = self.remove_words(
            command,
            ['whats', 'what', 'is', 'the']
        )

        res = mathparse.parse(math_command, language='ENG')

        response = math_command + f" is {round(res, 2)}"

        return response
    
    def remove_words(self, text: str, words: List[str]):
        for word in words:
            text = text.replace(word, '').strip()
        return text

def build_skill(config: Dict, ova: 'OpenVoiceAssistant'):
    return Mathparse(config, ova)

def default_config():
    return {
        "name": "MathParse"
        }