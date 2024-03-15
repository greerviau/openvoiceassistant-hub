import typing
import time
import threading
import random
import logging
logger = logging.getLogger("integration.open_weather_map")

from datetime import datetime, timedelta
from pyowm import OWM

class OpenWeatherMap:

    def __init__(self, integration_config: typing.Dict, ova: "OpenVoiceAssistant"):
        api_key = integration_config["api_key"]
        lat = ova.settings["latitude"]
        lon = ova.settings["longitude"]
        u_i = integration_config["update_interval"]
        use_one_call = "onecall" in u_i
        update_interval = 3600 if "hourly" in u_i else 86400

        owm = OWM(api_key)
        mgr = owm.weather_manager()

        def _update_weather():
            while True:
                self._weather = {}
                if use_one_call:
                    try:
                        oc = mgr.one_call(lat=lat, lon=lon)
                    except:
                        raise RuntimeError("Cannot make onecall requests with free API key")
                    self._weather["current"] = oc.current
                    self._weather["hourly_forecast"] = oc.forecast_hourly
                    self._weather["daily_forecast"] = oc.forecast_daily
                else:
                    self._weather["current"] = mgr.weather_at_coords(lat=lat, lon=lon).weather
                    self._weather["hourly_forecast"] = mgr.forecast_at_coords(lat=lat, lon=lon, interval="3h").forecast
                    try:
                        self._weather["daily_forecast"] = mgr.forecast_at_coords(lat=lat, lon=lon, interval="daily").forecast
                    except:
                        logger.warning("Cannot make daily forecast requests with free API key")

                today = {"morning": None, "afternoon": None, "evening": None}
                tomorrow = {"morning": None, "afternoon": None, "evening": None}
                for weather in self._weather["hourly_forecast"]:
                    dt = datetime.utcfromtimestamp(weather.ref_time).astimezone(ova.timezone)
                    logger.debug(dt)
                    if dt.day == datetime.today().day:
                        if dt.hour < 12 and dt.hour + 3 >= 12:
                            today["morning"]  = weather
                        elif dt.hour < 17 and dt.hour + 3 >= 17:
                            today["afternoon"] = weather
                        else:
                            today["evening"] = weather
                    elif dt.day == (datetime.today() + timedelta(days=1)).day:
                        if dt.hour < 12 and dt.hour + 3 >= 12:
                            tomorrow["morning"]  = weather
                        elif dt.hour < 17 and dt.hour + 3 >= 17:
                            tomorrow["afternoon"] = weather
                        else:
                            tomorrow["evening"] = weather
                    else:
                        break
                self._weather["today"] = today
                self._weather["tomorrow"] = tomorrow
                logger.debug(self._weather)
                logger.info("Current Location Weather Updated")
                time.sleep(update_interval)

        self.weather_thread = threading.Thread(target=_update_weather, daemon=True)
        self.weather_thread.start()

    def get_current_weather(self):
        return self._weather["current"]

    def get_hourly_forecast(self):
        return self._weather["hourly_forecast"]
    
    def get_daily_forecast(self):
        return self._weather["daily_forecast"]

    def get_morning_weather(self):
        return self._weather["today"]["morning"]

    def get_afternoon_weather(self):
        return self._weather["today"]["afternoon"]

    def get_evening_weather(self):
        return self._weather["today"]["evening"]

    def get_today_forecast(self):
        return self._weather["today"]

    def get_tomorrow_forecast(self):
        return self._weather["tomorrow"]
    
    def get_sky_conditions(self, weather):
        MAIN_STATUS_MAPPING = {
            "thunderstorm": ["thunderstorming"],
            "drizzle": ["drizzling"],
            "rain": ["raining"],
            "snow": ["snowing"],
            "clear": ["clear", "clear skies"]
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