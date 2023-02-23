import typing

class Weather:

    def weather(self, context):
        command = context['command']
        addr = context['addr'] if 'addr' in context else ''

        context['response'] = 'Not implemented'

    def sky(self, context):
        command = context['command']
        addr = context['addr'] if 'addr' in context else ''

        context['response'] = 'Not implemented'

    def air(self, context):
        command = context['command']
        addr = context['addr'] if 'addr' in context else ''

        context['response'] = 'Not implemented'

    def temperature(self, context):
        command = context['command']
        addr = context['addr'] if 'addr' in context else ''

        context['response'] = 'Not implemented'

    def ocean(self, context):
        command = context['command']
        addr = context['addr'] if 'addr' in context else ''

        context['response'] = 'Not implemented'

def build_skill(config: typing.Dict):
    return Weather()

def default_config():
    return {}