import typing
import time
import threading
import random
import logging
logger = logging.getLogger("skill.open_weather_map")

from datetime import datetime

RESPONSE_TEMPLATES = [
    "Right now it's %s",
    "Currently it's %s",
    "Outside it's %s",
    "It's currently %s"
]

class OpenWeatherMap:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova

        self.owm_integration = self.ova.integration_manager.get_integration_module('open_weather_map')

        self.unit = skill_config["temperature_unit"]

    def _preprocess_time_of_day(self, command, morning, afternoon, evening):
        if any(x in command.split() for x in ['morning']):
            afternoon, evening = None, None
        elif any(x in command.split() for x in ['afternoon']):
            morning, evening = None, None
        elif any(x in command.split() for x in ['tonight', 'evening']):
            morning, afternoon = None, None
        elif any(x in command.split() for x in ['later']):
            if morning:
                morning = None
            elif afternoon:
                afternoon = None
        return morning, afternoon, evening

    def _right_now(self, command: str):
        return any(x in command for x in ['right now', 'outside'])

    def weather_forecast(self, context: typing.Dict):
        command = context['cleaned_command']
        sentences = []

        weather = self.owm_integration.get_current_weather()
        sky = self.owm_integration.get_sky_conditions(weather)
        sentence = random.choice(RESPONSE_TEMPLATES) % (sky)

        temp_data = weather.temperature(self.unit)
        temp = int(temp_data["temp"]) 
        feels_like = int(temp_data["feels_like"])
        if abs(temp - feels_like) > 10:
            sentence += f" and {temp} degrees, but it feels like {feels_like}"
        else:
            sentence += f" and {temp} degrees"
        sentences.append(sentence)
        
        if not self._right_now(command):
            day_str = "This"
            if 'tomorrow' in command.split():
                sentences = []
                day_str = "Tomorrow"
                forecast = self.owm_integration.get_tomorrow_forecast()
            else:
                forecast = self.owm_integration.get_today_forecast()
            morning, afternoon, evening = forecast['morning'], forecast['afternoon'], forecast['evening']
            morning, afternoon, evening = self._preprocess_time_of_day(command, morning, afternoon, evening)
                
            if morning:
                sky = self.owm_integration.get_sky_conditions(morning)
                temp = int(morning.temperature(self.unit)["temp"])
                sentences.append(f"{day_str} morning it will be {temp} degrees and {sky}")
            if afternoon:
                sky = self.owm_integration.get_sky_conditions(afternoon)
                temp = int(afternoon.temperature(self.unit)["temp"])
                if not morning:
                    sentences.append(f"{day_str} afternoon it will be {temp} degrees and {sky}")
                else:
                    sentences.append(f"In the afternoon it will be {temp} degrees and {sky}")
            if evening:
                sky = self.owm_integration.get_sky_conditions(evening)
                temp = int(evening.temperature(self.unit)["temp"])
                if not afternoon:
                    sentences.append(f"{day_str} evening it will be {temp} degrees and {sky}")
                else:
                    sentences.append(f"In the evening it will be {temp} degrees and {sky}")

        context["response"] = ". ".join(sentences) + "."

    def sky_conditions(self, context: typing.Dict):
        command = context['cleaned_command']
        sentences = []

        weather = self.owm_integration.get_current_weather()
        sky = self.owm_integration.get_sky_conditions(weather)
        sentences.append(random.choice(RESPONSE_TEMPLATES) % (sky))

        if not self._right_now(command):
            day_str = "This"
            if 'tomorrow' in command.split():
                sentences = []
                day_str = "Tomorrow"
                forecast = self.owm_integration.get_tomorrow_forecast()
            else:
                forecast = self.owm_integration.get_today_forecast()
            morning, afternoon, evening = forecast['morning'], forecast['afternoon'], forecast['evening']
            morning, afternoon, evening = self._preprocess_time_of_day(command, morning, afternoon, evening)

            if morning:
                sky = self.owm_integration.get_sky_conditions(morning)
                sentences.append(f"{day_str} morning it will be {sky}")
            if afternoon:
                sky = self.owm_integration.get_sky_conditions(afternoon)
                if not morning:
                    sentences.append(f"{day_str} afternoon it will be {sky}")
                else:
                    sentences.append(f"In the afternoon it will be {sky}")
            if evening:
                sky = self.owm_integration.get_sky_conditions(evening)
                if not afternoon:
                    sentences.append(f"{day_str} evening it will be {sky}")
                else:
                    sentences.append(f"In the evening it will be {sky}")

        context["response"] = ". ".join(sentences) + "."
    
    def humidity(self, context: typing.Dict):
        command = context['cleaned_command']
        sentences = []

        weather = self.owm_integration.get_current_weather()
        humidity = int(weather.humidity)
        humidity_string = ""
        yes_no_string = ""
        if any(x in command.split() for x in ['muggy', 'humid', 'dry']):
            if humidity < 30:
                humidity_string = "very dry"
                if any(x in command.split() for x in ['muggy', 'humid']):
                    yes_no_string = "No"
                else:
                    yes_no_string = "Yes"
            elif humidity < 40:
                humidity_string = "fairly dry"
                if any(x in command.split() for x in ['muggy', 'humid']):
                    yes_no_string = "No"
                else:
                    yes_no_string = "Yes"
            elif humidity >= 40 and humidity <= 60:
                humidity_string = "quite comfortable"
                yes_no_string = "No"
            else:
                humidity_string = "very humid"
                if any(x in command.split() for x in ['muggy', 'humid']):
                    yes_no_string = "Yes"
                else:
                    yes_no_string = "No"
        else:  
            humidity_string = f"{humidity} percent humidity"

        if yes_no_string:
            sentences.append(yes_no_string)
        sentences.append(random.choice(RESPONSE_TEMPLATES) % (humidity_string))
        
        if not self._right_now(command):
            day_str = "This"
            if 'tomorrow' in command.split():
                sentences = []
                day_str = "Tomorrow"
                forecast = self.owm_integration.get_tomorrow_forecast()
            else:
                forecast = self.owm_integration.get_today_forecast()
            morning, afternoon, evening = forecast['morning'], forecast['afternoon'], forecast['evening']
            morning, afternoon, evening = self._preprocess_time_of_day(command, morning, afternoon, evening)

            if morning:
                humidity = int(weather.humidity)
                sentences.append(f"{day_str} morning it will be {humidity} percent humidity")
            if afternoon:
                humidity = int(weather.humidity)
                if not morning:
                    sentences.append(f"{day_str} afternoon it will be {humidity} percent humidity")
                else:
                    sentences.append(f"In the afternoon it will be {humidity} percent humidity")
            if evening:
                humidity = int(weather.humidity)
                if not afternoon:
                    sentences.append(f"{day_str} evening it will be {humidity} percent humidity")
                else:
                    sentences.append(f"In the evening it will be {humidity} percent humidity")

        context["response"] = ". ".join(sentences) + "."

    def temperature(self, context: typing.Dict):
        command = context['cleaned_command']
        sentences = []

        weather = self.owm_integration.get_current_weather()
        temp_data = weather.temperature(self.unit)
        temp = int(temp_data["temp"]) 
        feels_like = int(temp_data["feels_like"])

        temperature_string = ""
        yes_no_string = ""
        if any(x in command.split() for x in ['hot', 'warm', 'comfortable', 'cold', 'chilly']):
            measure_temp = int(weather.temperature('celsius')["temp"])
            if measure_temp < -7:   # ~20F
                temperature_string = "very cold"
                if any(x in command.split() for x in ['hot', 'warm', 'comfortable']):
                    yes_no_string = "No"
                else:
                    yes_no_string = "Yes"
            elif measure_temp < 5:  # ~40 F
                temperature_string = "cold"
                if any(x in command.split() for x in ['hot', 'warm', 'comfortable']):
                    yes_no_string = "No"
                else:
                    yes_no_string = "Yes"
            elif measure_temp < 10: # 50F
                temperature_string = "fairly cold"
                if any(x in command.split() for x in ['hot', 'warm', 'comfortable']):
                    yes_no_string = "No"
                else:
                    yes_no_string = "Yes"
            elif measure_temp >= 10 and measure_temp <= 24: # 50F - ~75F
                temperature_string = "quite comfortable"
                if any(x in command.split() for x in ['hot', 'chilly', 'cold']):
                    yes_no_string = "No"
                else:
                    yes_no_string = "Yes"
            elif measure_temp > 24 and measure_temp <= 32:  # ~75F - ~90F
                temperature_string = "warm"
                if any(x in command.split() for x in ['hot', 'chilly', 'cold']):
                    yes_no_string = "No"
                else:
                    yes_no_string = "Yes"
            else:
                if any(x in command.split() for x in ['warm', 'comfortable', 'chilly', 'cold']):
                    yes_no_string = "No"
                else:
                    yes_no_string = "Yes"
                temperature_string = "very hot" 
        else:
            temperature_string = f"{temp} degrees"
            if abs(temp - feels_like) > 10:
                temperature_string += f", but it feels like {feels_like}"

        if yes_no_string:
            sentences.append(yes_no_string)
        sentences.append(random.choice(RESPONSE_TEMPLATES) % (temperature_string))

        if not self._right_now(command):
            day_str = "This"
            if 'tomorrow' in command.split():
                sentences = []
                day_str = "Tomorrow"
                forecast = self.owm_integration.get_tomorrow_forecast()
            else:
                forecast = self.owm_integration.get_today_forecast()
            morning, afternoon, evening = forecast['morning'], forecast['afternoon'], forecast['evening']
            morning, afternoon, evening = self._preprocess_time_of_day(command, morning, afternoon, evening)

            if morning:
                temp = int(morning.temperature(self.unit)["temp"])
                sentences.append(f"{day_str} morning it will be {temp} degrees")
            if afternoon:
                temp = int(afternoon.temperature(self.unit)["temp"])
                if not morning:
                    sentences.append(f"{day_str} afternoon it will be {temp} degrees")
                else:
                    sentences.append(f"In the afternoon it will be {temp} degrees")
            if evening:
                temp = int(evening.temperature(self.unit)["temp"])
                if not afternoon:
                    sentences.append(f"{day_str} evening it will be {temp} degrees")
                else:
                    sentences.append(f"In the evening it will be {temp} degrees")

        context["response"] = ". ".join(sentences) + "."