from typing import Dict

from backend import config

class Greetings:

    def __init__(self, config: Dict, ova: 'OpenVoiceAssistant'):
        self.config = config

    def hello(self, context: Dict):
        command = context['cleaned_command']
        addr = context['addr'] if 'addr' in context else ''

        response = ''
        if 'morning' in command:
            response = f'Good morning {addr}'
        elif 'afternoon' in command:
            response = f'Good afternoon {addr}'
        elif 'evening' in command:
            response = f'Good evening {addr}'
        elif 'night' in command:
            response = f'Good night {addr}'
        else:
            response = f'Hello {addr}'

        return response

    def how_are_you(self, context: Dict):
        command = context['cleaned_command']
        addr = context['addr'] if 'addr' in context else ''

        response = f'Doing well {addr}'

        return response

    def whats_up(self, context: Dict):
        command = context['cleaned_command']
        addr = context['addr'] if 'addr' in context else ''

        response = f'Not much {addr}'
        
        return response

    def goodbye(self, context: Dict):
        command = context['cleaned_command']
        addr = context['addr'] if 'addr' in context else ''

        response = f'Goodbye {addr}'

        return response

def build_skill(config: Dict, ova: 'OpenVoiceAssistant'):
    return Greetings(config, ova)

def default_config():
    return {}