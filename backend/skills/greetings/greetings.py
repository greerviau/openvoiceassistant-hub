import typing

from backend.config import Configuration

class Greetings:

    def hello(self, context: typing.Dict):
        command = context['command']
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
        context['response'] = response

    def how_are_you(self, context: typing.Dict):
        command = context['command']
        addr = context['addr'] if 'addr' in context else ''

        response = f'Doing well {addr}'
        context['response'] = response

    def whats_up(self, context: typing.Dict):
        command = context['command']
        addr = context['addr'] if 'addr' in context else ''

        response = f'Not much {addr}'
        context['response'] = response

    def goodbye(self, context: typing.Dict):
        command = context['command']
        addr = context['addr'] if 'addr' in context else ''

        response = f'Goodbye {addr}'
        context['response'] = response

def build_skill(config: Configuration):
    return Greetings()

def default_config():
    return {}