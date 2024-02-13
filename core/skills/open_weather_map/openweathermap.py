import typing
import time
import threading
import random
from pyowm import OWM

class OpenWeatherMap:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova

        self.owm_integration = self.ova.integration_manager.get_integration_module('open_weather_map')

        self.unit = skill_config["temperature_unit"]

    def weather(self, context: typing.Dict):
        weather = self.owm_integration.get_current_weather()
        command = context["command"]

        sky = self.__sky(context)
        temp = int(weather.temperature(self.unit)["temp"])
        humidity = int(weather.humidity)

        context['response'] = f"{sky}. The temperature is {temp} degrees with a humidity of {humidity} percent."

    def __sky(self, context: typing.Dict):
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
            "Outside it's %s"
        ]

        weather = self.owm_integration.get_current_weather()

        main_status = weather.status.lower()
        detailed_status = weather.detailed_status.lower()

        if main_status in list(MAIN_STATUS_MAPPING.keys()):
            condition = random.choice(MAIN_STATUS_MAPPING[main_status])
        else:
            condition = random.choice(DETAILED_STATUS_MAPPING[detailed_status])

        return (random.choice(RESPONSE_TEMPLATES) % (condition))

    def sky(self, context: typing.Dict):
        context['response'] = self.__sky(context)

    def air(self, context: typing.Dict):
        RESPONSE_TEMPLATES = [
            "Today will be %s",
            "It is %s outside",
            "Its currently %s right now"
        ]

        weather = self.owm_integration.get_current_weather()

        humidity = int(weather.humidity)

        template = random.choice(RESPONSE_TEMPLATES)

        context['response'] = template % (f"{humidity} percent humidity")

    def temperature(self, context: typing.Dict):
        RESPONSE_TEMPLATES = [
            "Today will be %s",
            "It is %s outside",
            "Its currently %s right now"
        ]

        weather = self.owm_integration.get_current_weather()

        temp = int(weather.temperature(self.unit)["temp"])

        template = random.choice(RESPONSE_TEMPLATES)

        context['response'] = template % (f"{temp} degrees")

def build_skill(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    return OpenWeatherMap(skill_config, ova)

def default_config():
    return {
        "temperature_unit": "fahrenheit",
        "temperature_unit_options": ["fahrenheit", "celsius"],
        "required_integrations": ["open_weather_map"]
    }