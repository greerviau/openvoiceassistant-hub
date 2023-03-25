import typing

class Weather:

    def __init__(self, config: typing.Dict):
        self.owm_base_url = "http://api.openweathermap.org/data/2.5/weather?"
        self.owm_api_key = config["owm_api_key"]
        self.city = config["city"]

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
    return Weather(config)

def default_config():
    return {
        "owm_api_key": "",
        "city": ""
    }