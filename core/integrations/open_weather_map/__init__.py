import typing

def build_integration(skill_config: typing.Dict, ova: "OpenVoiceAssistant"):
    from .open_weather_map import OpenWeatherMap
    return OpenWeatherMap(skill_config, ova)

def manifest():
    return {
        "name": "Open Weather Map",
        "id": "open_weather_map",
        "category": "weather",
        "requirements": ["pyowm==3.3.0"],
        "config": {
            "api_key": "",
            "latitude": 0,
            "longitude": 0,
            "update_interval": "hourly",
            "update_interval_options": ["hourly", "daily", "onecall_hourly", "onecall_daily"]
        }
    }