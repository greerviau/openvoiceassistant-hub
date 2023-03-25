from typing import Dict
import urllib
import requests
import time
import threading

class Weather:

    def __init__(self, config: Dict):
        self.config = config
        self.owm_base_url = "http://api.openweathermap.org/data/2.5/"
        self.owm_api_key = config["owm_api_key"]
        lat = config["latitude"]
        lon = config["longitude"]
        query = f"onecall?lat={lat}&lon={lon}&appid={self.owm_api_key}&units=metric"
        self.owm_query_url = urllib.parse.urljoin(self.owm_base_url, query)
        self.update_delay_seconds = config["update_delay_seconds"]

        self.weather_data = None

        update_thread = threading.Thread(target=self._weather_thread)

    def _weather_thread(self):
        while True:
            response = requests.get(self.owm_query_url)
            self.weather_data = response
            time.sleep(self.update_delay_seconds)

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
        "latitude": "",
        "longitude": "",
        "update_delay_seconds": 3600
    }