from typing import Dict
import urllib
import requests
import time
import threading
from datetime import datetime
import random
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
        forecast_query = f"forecast?{query_params}"

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

            dt = datetime.strptime(chunk["dt_txt"], "%Y-%m-%d %H:%M:%S")

            parsed_chunk["datetime"] = dt

            parsed_chunk["weather"] = chunk["weather"]
            parsed_chunk["temp"] = chunk["main"]["temp"]
            parsed_chunk["feels_like"] = chunk["main"]["feels_like"]
            parsed_chunk["temp_min"] = chunk["main"]["temp_min"]
            parsed_chunk["temp_max"] = chunk["main"]["temp_max"]
            parsed_chunk["pressure"] = chunk["main"]["pressure"]
            parsed_chunk["humidity"] = chunk["main"]["humidity"]
            parsed_chunk["wind_speed"] = chunk["wind"]["speed"]

            parsed["forecast"].append(parsed_chunk)

        parsed["city"] = data["city"]["name"]
        parsed["country"] = data["city"]["country"]

        return parsed

    def _weather_thread(self):
        while not self.event.is_set():
            print('Querying OWM for current weather')
            response = requests.get(self.owm_weather_query_url)
            #print('Weather data')
            #print(response.json())
            self.weather_data = self._parse_weather_data(response.json())

            print('Querying OWM for todays forecast')
            response = requests.get(self.owm_forecast_query_url)
            #print('Forecast data')
            #print(response.json())
            self.forecast_data = self._parse_forecast_data(response.json())

            print('Waiting...')
            time.sleep(self.update_delay_seconds)

    def __del__(self):
        self.event.set()

    def weather(self, context: Dict):
        command = context['command']

        sky = self.sky(context)
        temp = int(self.weather_data["temp"])
        humidity = int(self.weather_data["humidity"])

        response = f"{sky}. The tempurature is {temp} degrees. The humidity is {humidity} percent."

        return response

    def sky(self, context: Dict):
        SKY_MAPPING = {
            "clouds": ["overcast", "cloudy"],
            "rain": ["raining", "rainy"],
            "snow": ["snowing"],
            "clear": ["clear", "sunny"]
        }

        RESPONSE_TEMPLATES = [
            "It looks like its %s outside",
            "Today will be %s"
            "It is %s outside",
            "Its currently %s right now"
        ]

        command = context['command']

        s = self.weather_data["weather"][0]["main"].lower()

        condition = random.choice(SKY_MAPPING[s])

        response = random.choice(RESPONSE_TEMPLATES) % (condition)

        return response

    def air(self, context: Dict):
        RESPONSE_TEMPLATES = [
            "Today will be %s"
            "It is %s outside",
            "Its currently %s right now"
        ]

        command = context['command']

        humidity = int(self.weather_data["humidity"])

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
            "Today will be %s"
            "It is %s outside",
            "Its currently %s right now"
        ]

        command = context['command']

        temp = int(self.weather_data["temp"])

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
        "latitude": "",
        "longitude": "",
        "update_delay_seconds": 3600,
        "unit": "imperial",
        "units": ["imperial", "metric"]
    }