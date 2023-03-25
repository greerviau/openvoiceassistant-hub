from typing import Dict

class Weather:

    def __init__(self, config: Dict):
        self.config = config
        self.owm_base_url = "http://api.openweathermap.org/data/2.5/weather?"
        self.owm_api_key = config["owm_api_key"]
        self.city = config["city"]

    def weather(self, context: Dict):
        command = context['command']
        addr = context['addr'] if 'addr' in context else ''

        context['response'] = 'Not implemented'

    def sky(self, context: Dict):
        command = context['command']
        addr = context['addr'] if 'addr' in context else ''

        context['response'] = 'Not implemented'

    def air(self, context: Dict):
        command = context['command']
        addr = context['addr'] if 'addr' in context else ''

        context['response'] = 'Not implemented'

    def temperature(self, context: Dict):
        command = context['command']
        addr = context['addr'] if 'addr' in context else ''

        context['response'] = 'Not implemented'

    def ocean(self, context: Dict):
        command = context['command']
        addr = context['addr'] if 'addr' in context else ''

        context['response'] = 'Not implemented'

def build_skill(config: Dict):
    return Weather(config)

def default_config():
    return {
        "owm_api_key": "",
        "city": ""
    }