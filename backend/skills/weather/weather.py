from typing import Dict
import time
import threading
import random
from pyowm import OWM
from typing import Dict

class Weather:

    def __init__(self, config: Dict, ova: 'OpenVoiceAssistant'):
        self.config = config

        owm_api_key = config["owm_api_key"]
        self.lat = config["latitude"]
        self.lon = config["longitude"]
        self.unit = config["unit"]

        owm = OWM(owm_api_key)
        self.mgr = owm.weather_manager()

    def _get_weather(self, context: Dict):
        ents = context["pos_info"]["ENTITIES"]
        location = ents["GPE"] if "GPE" in ents else ents["PERSON"] if "PERSON" in ents else None
        if location:
            return self.mgr.weather_at_place(location).weather, f" in {location}"
        else:
            return self.mgr.weather_at_coords(lat=self.lat, lon=self.lon).weather, ""

    def weather(self, context: Dict):
        w, loc = self._get_weather(context)

        sky = self.sky(context)
        temp = int(w.temperature(self.unit)["temp"])
        humidity = int(w.humidity)

        response = f"{sky}. The temperature is {temp} degrees with a humidity of {humidity} percent."

        return response

    def sky(self, context: Dict):
        SKY_MAPPING = {
            "clouds": ["cloudy"],
            "overcast clouds": ["overcast"],
            "few clouds": ["mostly clear"],
            "scattered clouds": ["scattered clouds"],
            "broken clouds": ["broken clouds"],
            "rain": ["raining", "rainy"],
            "snow": ["snowing"],
            "clear sky": ["clear", "sunny"],
            "mist": ["misty"],
            "moderate rain": ["moderate rain"],
            "haze": ["hazy"]
        }

        RESPONSE_TEMPLATES = [
            "It looks like it's %s outside",
            "Today it will be %s",
            "It is %s outside",
            "It's %s right now"
        ]

        w, loc = self._get_weather(context)

        status = w.detailed_status

        condition = random.choice(SKY_MAPPING[status])

        response = (random.choice(RESPONSE_TEMPLATES) % (condition)) + loc

        return response

    def air(self, context: Dict):
        RESPONSE_TEMPLATES = [
            "Today will be %s",
            "It is %s outside",
            "Its currently %s right now"
        ]

        w, loc = self._get_weather(context)

        humidity = int(w.humidity)

        feeling = "dry"

        if humidity > 20:
            feeling = "comfortable"
            if humidity > 60:
                feeling = "muggy"

        template = random.choice(RESPONSE_TEMPLATES)

        if random.choice([0,1]):
            response = (template % (feeling)) + loc
        else:
            response = template % (f"{humidity} percent humidity") + loc

        return response

    def temperature(self, context: Dict):
        RESPONSE_TEMPLATES = [
            "Today will be %s",
            "It is %s outside",
            "Its currently %s right now"
        ]

        w, loc = self._get_weather(context)

        temp = int(w.temperature(self.unit)["temp"])

        feeling = "cold"

        if temp > 55:
            feeling = "comfortable"
            if temp > 80:
                feeling = "hot"

        template = random.choice(RESPONSE_TEMPLATES)

        if random.choice([0,1]):
            response = template % (feeling) + loc
        else:
            response = template % (f"{temp} degrees") + loc

        return response

    def ocean(self, context: Dict):
        w, loc = self._get_weather(context)

        response = "Not implemented"

        return response

def build_skill(config: Dict, ova: 'OpenVoiceAssistant'):
    return Weather(config, ova)

def default_config():
    return {
        "owm_api_key": "",
        "latitude": 0,
        "longitude": 0,
        "unit": "fahrenheit",
        "unit_options": ["fahrenheit", "celsius"]
    }