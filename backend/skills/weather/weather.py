from typing import Dict
import urllib
import requests
import time
import threading
from datetime import datetime
import random
from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps
from typing import Dict

class Weather:

    def __init__(self, config: Dict):
        self.config = config

        owm_api_key = config["owm_api_key"]
        self.lat = config["latitude"]
        self.lon = config["longitude"]
        self.unit = config["unit"]
        self.update_delay_seconds = config["update_delay_seconds"]

        owm = OWM(owm_api_key)
        self.mgr = owm.weather_manager()

        self.w = None

        self.event = threading.Event()

        weather_thread = threading.Thread(target=self._weather_thread)
        weather_thread.start()

    def _weather_thread(self):
        while not self.event.is_set():
            self.w = self.mgr.weather_at_coords(lat=self.lat, lon=self.lon).weather

            print('Waiting...')
            time.sleep(self.update_delay_seconds)

    def __del__(self):
        self.event.set()

    def weather(self, context: Dict):
        command = context['command']

        sky = self.sky(context)
        temp = int(self.w.temperature(self.unit)["temp"])
        humidity = int(self.w.humidity)

        response = f"{sky}. The temperature is {temp} degrees. The humidity is {humidity} percent."

        return response

    def sky(self, context: Dict):
        SKY_MAPPING = {
            "clouds": ["overcast", "cloudy"],
            "few clouds": ["mostly clear", "scattered clouds"],
            "rain": ["raining", "rainy"],
            "snow": ["snowing"],
            "clear": ["clear", "sunny"]
        }

        RESPONSE_TEMPLATES = [
            "It looks like its %s outside",
            "Today it will be %s",
            "It is %s outside",
            "Its currently %s right now"
        ]

        command = context['command']

        status = self.w.detailed_status

        condition = random.choice(SKY_MAPPING[status])

        response = random.choice(RESPONSE_TEMPLATES) % (condition)

        return response

    def air(self, context: Dict):
        RESPONSE_TEMPLATES = [
            "Today will be %s",
            "It is %s outside",
            "Its currently %s right now"
        ]

        command = context['command']

        humidity = int(self.w.humidity)

        feeling = "dry"

        if humidity > 20:
            feeling = "comfortable"
            if humidity > 60:
                feeling = "muggy"

        template = random.choice(RESPONSE_TEMPLATES)

        if random.choice([0,1]):
            response = template % (feeling)
        else:
            response = template % (f"{humidity} percent humidity")

        return response

    def temperature(self, context: Dict):
        RESPONSE_TEMPLATES = [
            "Today will be %s",
            "It is %s outside",
            "Its currently %s right now"
        ]

        command = context['command']

        temp = int(self.w.temperature(self.unit)["temp"])

        feeling = "cold"

        if temp > 55:
            feeling = "comfortable"
            if temp > 80:
                feeling = "hot"

        template = random.choice(RESPONSE_TEMPLATES)

        if random.choice([0,1]):
            response = template % (feeling)
        else:
            response = template % (f"{temp} degrees")

        return response

    def ocean(self, context: Dict):
        command = context['command']

        response = "Not implemented"

        return response

def build_skill(config: Dict):
    return Weather(config)

def default_config():
    return {
        "owm_api_key": "",
        "latitude": 0,
        "longitude": 0,
        "update_delay_seconds": 3600,
        "unit": "fahrenheit",
        "unit_choices": ["fahrenheit ", "celsius"]
    }