import typing
import time
import threading
import random
from datetime import datetime
from pyowm import OWM

RESPONSE_TEMPLATES = [
    "Right now it's %s",
    "Currently it's %s"
    "It is %s outside",
    "It's currently %s"
]

class OpenWeatherMap:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova

        self.owm_integration = self.ova.integration_manager.get_integration_module('open_weather_map')

        self.unit = skill_config["temperature_unit"]

    def weather_current(self, context: typing.Dict):
        weather = self.owm_integration.get_current_weather()
        sky_conditions = self.owm_integration.get_sky_conditions(weather)
        temp_data = weather.temperature(self.unit)
        temp = int(temp_data["temp"]) 
        feels_like = int(temp_data["feels_like"])
        if abs(temp - feels_like) > 10:
            temp_response = f"It's {temp} degrees, but it feels like {feels_like}"
        else:
            temp_response = f"It's {temp} degrees"
        humidity = int(weather.humidity)
        context["response"] = f"Right now it's {sky_conditions} outside. {temp_response}, with a {humidity} percent humidity"

    def weather_forecast(self, context: typing.Dict):
        morning, afternoon, evening = self.owm_integration.get_full_day_forecast()

        response = ""
        if morning:
            sky = self.owm_integration.get_sky_conditions(morning)
            temp = int(morning.temperature(self.unit)["temp"])
            response += f"This morning it will be {temp} degrees and {sky}. "
        if afternoon:
            sky = self.owm_integration.get_sky_conditions(afternoon)
            temp = int(afternoon.temperature(self.unit)["temp"])
            if not morning:
                response += f"This afternoon it will be {temp} degrees and {sky}. "
            else:
                response += f"In the afternoon it will be {temp} degrees and {sky}. "
        if evening:
            sky = self.owm_integration.get_sky_conditions(evening)
            temp = int(evening.temperature(self.unit)["temp"])
            if not afternoon or morning:
                response += f"This evening it will be {temp} degrees and {sky}. "
            else:
                response += f"In the evening it will be {temp} degrees and {sky}. "
        context["response"] = response

    def sky_current(self, context: typing.Dict):
        weather = self.owm_integration.get_current_weather()
        sky_conditions = self.owm_integration.get_sky_conditions(weather)

        template = random.choice(RESPONSE_TEMPLATES)
        context['response'] = template % (sky_conditions)

    def sky_forecast(self, context: typing.Dict):
        morning, afternoon, evening = self.owm_integration.get_full_day_forecast()

        response = ""
        if morning:
            sky = self.owm_integration.get_sky_conditions(morning)
            response += f"This morning it will be {sky}. "
        if afternoon:
            sky = self.owm_integration.get_sky_conditions(afternoon)
            if not morning:
                response += f"This afternoon it will be {sky}. "
            else:
                response += f"In the afternoon it will be {sky}. "
        if evening:
            sky = self.owm_integration.get_sky_conditions(evening)
            if not afternoon or morning:
                response += f"This evening it will be {sky}. "
            else:
                response += f"In the evening it will be {sky}. "
        context["response"] = response

    def humidity_current(self, context: typing.Dict):
        command = context['cleaned_command']
        weather = self.owm_integration.get_current_weather()
        humidity = int(weather.humidity)

        if any(x in command.split() for x in ['muggy', 'humid', 'dry']):
            if humidity < 30:
                humidity_string = "very dry"
            elif humidity < 40:
                humidity_string = "fairly dry",
            elif humidity >= 40 and humidity <= 60:
                humidity_string = "quite comfortable"
            else:
                humidity_string = "very humid"
        else:  
            humidity_string = f"{humidity} percent humidity"

        template = random.choice(RESPONSE_TEMPLATES)
        context['response'] = template % (humidity_string)
    
    def humidity_forecast(self, context: typing.Dict):
        morning, afternoon, evening = self.owm_integration.get_full_day_forecast()

        response = ""
        if morning:
            humidity = int(weather.humidity)
            response += f"This morning it will be {humidity} percent humidity. "
        if afternoon:
            humidity = int(weather.humidity)
            if not morning:
                response += f"This afternoon it will be {humidity} percent humidity. "
            else:
                response += f"In the afternoon it will be {humidity} percent humidity. "
        if evening:
            humidity = int(weather.humidity)
            if not afternoon or morning:
                response += f"This evening it will be {humidity} percent humidity. "
            else:
                response += f"In the evening it will be {humidity} percent humidity. "
        context["response"] = response

    def temperature_current(self, context: typing.Dict):
        command = context['cleaned_command']
        weather = self.owm_integration.get_current_weather()
        temp_data = weather.temperature(self.unit)
        temp = int(temp_data["temp"]) 
        feels_like = int(temp_data["feels_like"])
        if abs(temp - feels_like) > 10:
            temp_response = f"It's {temp} degrees but it feels like {feels_like}"
        else:
            temp_response = f"It's {temp} degrees"

        if any(x in command.split() for x in ['hot', 'warm', 'cold', 'chilly', 'comfortable']):
            measure_temp = weather.temperature('celsius')
            if measure_temp < -7:   # ~20F
                temperature_string = "very cold"
            elif measure_temp < 5:  # ~40 F
                temperature_string = "cold"
            elif measure_temp < 10: # 50F
                temperature_string = "fairly cold",
            elif measure_temp >= 10 and measure_temp <= 24: # 50F - ~75F
                temperature_string = "quite comfortable"
            elif measure_temp > 24 and measure_temp <= 32:  # ~75F - ~90F
                temperature_string = "warm"
            else:
                temperature_string = "very hot" 
        else:
            temperature_string = f"{temp} degrees"
            if abs(temp - feels_like) > 10:
                temperature_string += f", but it feels like {feels_like}"

        template = random.choice(RESPONSE_TEMPLATES)
        context['response'] = template % (temperature_string)

    def temperature_forecast(self, context: typing.Dict):
        response = ""
        if morning:
            temp = int(morning.temperature(self.unit)["temp"])
            response += f"This morning it will be {temp} degrees. "
        if afternoon:
            temp = int(afternoon.temperature(self.unit)["temp"])
            if not morning:
                response += f"This afternoon it will be {temp} degrees. "
            else:
                response += f"In the afternoon it will be {temp} degrees. "
        if evening:
            temp = int(evening.temperature(self.unit)["temp"])
            if not afternoon or morning:
                response += f"This evening it will be {temp} degrees. "
            else:
                response += f"In the evening it will be {temp} degrees. "
        context["response"] = response

def build_skill(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    return OpenWeatherMap(skill_config, ova)

def default_config():
    return {
        "temperature_unit": "fahrenheit",
        "temperature_unit_options": ["fahrenheit", "celsius", "kelvin"],
        "required_integrations": ["open_weather_map"]
    }