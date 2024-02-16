import typing
import time
import threading
import random
from datetime import datetime
from pyowm import OWM

class OpenWeatherMap:

    def __init__(self, integration_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova

        api_key = integration_config["api_key"]
        lat = integration_config["latitude"]
        lon = integration_config["longitude"]
        u_i = integration_config["update_interval"]
        use_one_call = 'onecall' in u_i
        update_interval = 3600 if 'hourly' in u_i else 86400

        owm = OWM(api_key)
        mgr = owm.weather_manager()

        self._current_weather = None
        self._hourly_forecast = None
        self._daily_forecast = None
        
        self._morning_weather = None
        self._afternoon_weather = None
        self._evening_weather = None

        def _update_weather():
            while True:
                if use_one_call:
                    try:
                        oc = mgr.one_call(lat=lat, lon=lon)
                    except:
                        raise RuntimeError("Cannot make onecall requests with free API key")
                    self._current_weather = oc.current
                    self._hourly_forecast = oc.forecast_hourly
                    self._daily_forecast = oc.forecast_daily
                else:
                    self._current_weather = mgr.weather_at_coords(lat=lat, lon=lon).weather
                    self._hourly_forecast = mgr.forecast_at_coords(lat=lat, lon=lon, interval='3h').forecast
                    try:
                        self._daily_forecast = mgr.forecast_at_coords(lat=lat, lon=lon, interval='daily').forecast
                    except:
                        print("Cannot make daily forecast requests with free API key")

                for weather in self._hourly_forecast:
                    print(weather.ref_time)
                    dt = datetime.fromtimestamp(weather.ref_time)
                    print(dt)
                    if dt.day > datetime.today().day:
                        break
                    if dt.hour < 12 and dt.hour + 3 > 12:
                        self._morning_weather = weather
                    elif dt.hour < 17 and dt.hour + 3 > 17:
                        self._afternoon_weather = weather
                    else:
                        self._evening_weather = weather
                print("Current Location Weather Updated")
                time.sleep(update_interval)

        self.weather_thread = threading.Thread(target=_update_weather, daemon=True)
        self.weather_thread.start()

    def get_current_weather(self):
        return self._current_weather

    def get_hourly_forecast(self):
        return self._hourly_forecast
    
    def get_daily_forecast(self):
        return self._daily_forecast

    def get_morning_weather(self):
        return self._morning_weather

    def get_afternoon_weather(self):
        return self._afternoon_weather

    def get_evening_weather(self):
        return self._evening_weather

    def get_full_day_forecast(self):
        return self._morning_weather, self._afternoon_weather ,self._evening_weather
    
    def get_sky_conditions(self, weather):
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
            "squall": ["slightly stormy", "a squall"],
            "tornado": ["a tornado"],
        }

        main_status = weather.status.lower()
        detailed_status = weather.detailed_status.lower()

        if main_status in list(MAIN_STATUS_MAPPING.keys()):
            condition = random.choice(MAIN_STATUS_MAPPING[main_status])
        else:
            condition = random.choice(DETAILED_STATUS_MAPPING[detailed_status])

        return condition

def build_integration(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    return OpenWeatherMap(skill_config, ova)

def default_config():
    return {
        "api_key": "",
        "latitude": 0,
        "longitude": 0,
        "update_interval": "hourly",
        "update_interval_options": ["hourly", "daily", "onecall_hourly", "onecall_daily"]
    }