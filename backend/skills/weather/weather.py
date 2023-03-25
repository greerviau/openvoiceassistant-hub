from typing import Dict
import urllib
import requests
import time
import threading
import datetime
from typing import Dict

class Weather:

    def __init__(self, config: Dict):
        self.config = config

        self.owm_base_url = "http://api.openweathermap.org/data/2.5/"
        self.owm_api_key = config["owm_api_key"]

        lat = config["latitude"]
        lon = config["longitude"]
        unit = config["unit"]

        query_params = f"lat={lat}&lon={lon}&appid={self.owm_api_key}&units={unit}"

        weather_query = f"weather?{query_params}"
        forecast_query = f"weather?{query_params}"

        self.owm_weather_query_url = urllib.parse.urljoin(self.owm_base_url, weather_query)
        self.owm_forecast_query_url = urllib.parse.urljoin(self.owm_base_url, forecast_query)

        self.update_delay_seconds = config["update_delay_seconds"]

        self.weather_data = None
        self.forecast_data = None

        self.event = threading.Event()

        weather_thread = threading.Thread(target=self._weather_thread)
        weather_thread.start()

    def _parse_weather_data(self, data: Dict):
        parsed = {}

        parsed["weather"] = data["weather"]
        parsed["temp"] = data["main"]["temp"]
        parsed["feels_like"] = data["main"]["feels_like"]
        parsed["temp_min"] = data["main"]["temp_min"]
        parsed["temp_max"] = data["main"]["temp_max"]
        parsed["pressure"] = data["main"]["pressure"]
        parsed["humidity"] = data["main"]["humidity"]
        parsed["wind_speed"] = data["wind"]["speed"]
        parsed["country"] = data["sys"]["country"]
        parsed["city"] = data["name"]

        return parsed

    def _parse_forecast_data(self, data: Dict):
        parsed = {}
        parsed["forecast"] = []

        for chunk in data["list"]:
            parsed_chunk = {}

            dt = datetime.strptime(data["dt_txt"], "%y-%m-%d %H:%M:%S")

            parsed_chunk["datetime"] = dt

            parsed_chunk["weather"] = data["weather"]
            parsed_chunk["temp"] = data["main"]["temp"]
            parsed_chunk["feels_like"] = data["main"]["feels_like"]
            parsed_chunk["temp_min"] = data["main"]["temp_min"]
            parsed_chunk["temp_max"] = data["main"]["temp_max"]
            parsed_chunk["pressure"] = data["main"]["pressure"]
            parsed_chunk["humidity"] = data["main"]["humidity"]
            parsed_chunk["wind_speed"] = data["wind"]["speed"]

            parsed["forecast"].append(parsed_chunk)

        parsed["city"] = data["city"]["name"]
        parsed["country"] = data["city"]["country"]

        return parsed

    def _weather_thread(self):
        while not self.event.is_set():
            print('Querying OWM for current weather')
            response = requests.get(self.owm_weather_query_url)
            print('Weather data')
            print(response.json())
            self.weather_data = self._parse_weather_data(response.json())

            print('Querying OWM for todays forecast')
            response = requests.get(self.owm_forecast_query_url)
            print('Forecast data')
            print(response.json())
            self.forecast_data = self._parse_forecast_data(response.json())

            print('Waiting...')
            time.sleep(self.update_delay_seconds)

    def __del__(self):
        self.event.set()

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
        "update_delay_seconds": 3600,
        "unit": "imperial",
        "units": ["imperial", "metric"]
    }