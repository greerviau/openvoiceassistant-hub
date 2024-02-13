import typing
import time
import threading
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
                        raise RuntimeError("Cannot make daily forecast requests with free API key")
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