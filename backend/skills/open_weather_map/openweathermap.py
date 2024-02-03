import typing
import time
import threading
import random
from pyowm import OWM

class OpenWeatherMap:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova

        api_key = skill_config["api_key"]
        self.lat = skill_config["latitude"]
        self.lon = skill_config["longitude"]
        self.unit = skill_config["unit"]

        owm = OWM(api_key)
        self.mgr = owm.weather_manager()

        self._current_weather = None

        def _update_weather():
            while True:
                self._current_weather = self.mgr.weather_at_coords(lat=self.lat, lon=self.lon).weather
                print("Current Location Weather Updated")
                time.sleep(3600) # Wait 1 hour

        self.weather_thread = threading.Thread(target=_update_weather, daemon=True)
        self.weather_thread.start()

    def _get_weather(self, context: typing.Dict):
        ents = context["pos_info"]["ENTITIES"]
        location = ents["GPE"] if "GPE" in ents else ents["PERSON"] if "PERSON" in ents else None
        if location:
            return self.mgr.weather_at_place(location).weather, f" in {location}"
        else:
            return self._current_weather, ""

    def weather(self, context: typing.Dict):
        w, loc = self._get_weather(context)
        command = context["command"]

        sky = self.sky(context)
        temp = int(w.temperature(self.unit)["temp"])
        humidity = int(w.humidity)

        response = f"{sky}. The temperature{loc} is {temp} degrees with a humidity of {humidity} percent."

        return response

    def sky(self, context: typing.Dict):
        MAIN_STATUS_MAPPING = {
            "thunderstorm": ["thunderstorming"],
            "drizzle": ["drizzling"],
            "rain": ["raining"],
            "snow": ["snowing"],
            "clear": ["sunny", "clear", "clear skies"]
        }
        DETAILED_STATUS_MAPPING = {
            "few clouds": ["mostly clear"],
            "scattered clouds": ["scattered clouds"],
            "broken clouds": ["broken clouds"],
            "overcast clouds": ["overcast"],
            "mist": ["misty"],
            "smoke": ["smokey"],
            "haze": ["hazy"],
            "dust": ["dusty"],
            "fog": ["foggy"],
            "sand": ["sandy"],
            "ash": ["ashy"],
            "squall": ["slightly stormy"],
            "tornado": ["a tornado"],
        }

        RESPONSE_TEMPLATES = [
            "It looks like it's %s outside",
            "It appears to be %s outside",
            "It's %s outside",
            "It's %s right now",
            "Right now it's %s outside",
            "Right now it's %s",
            "Outside it's %s",

        ]

        w, loc = self._get_weather(context)

        main_status = w.status.lower()
        detailed_status = w.detailed_status.lower()

        if main_status in list(MAIN_STATUS_MAPPING.keys()):
            condition = random.choice(MAIN_STATUS_MAPPING[main_status])
        else:
            condition = random.choice(DETAILED_STATUS_MAPPING[detailed_status])

        response = (random.choice(RESPONSE_TEMPLATES) % (condition)) + loc

        return response

    def air(self, context: typing.Dict):
        RESPONSE_TEMPLATES = [
            "Today will be %s",
            "It is %s outside",
            "Its currently %s right now"
        ]

        w, loc = self._get_weather(context)

        humidity = int(w.humidity)

        template = random.choice(RESPONSE_TEMPLATES)

        response = template % (f"{humidity} percent humidity") + loc

        return response

    def temperature(self, context: typing.Dict):
        RESPONSE_TEMPLATES = [
            "Today will be %s",
            "It is %s outside",
            "Its currently %s right now"
        ]

        w, loc = self._get_weather(context)

        temp = int(w.temperature(self.unit)["temp"])

        template = random.choice(RESPONSE_TEMPLATES)

        response = template % (f"{temp} degrees") + loc

        return response

def build_skill(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    return OpenWeatherMap(skill_config, ova)

def default_config():
    return {
        "api_key": "",
        "latitude": 0,
        "longitude": 0,
        "unit": "fahrenheit",
        "unit_options": ["fahrenheit", "celsius"]
    }