import typing

INTENTIONS = [
    {
        "action": "weather_forecast",
        "patterns": [
            "whats the weather",
            "whats the weather right now",
            "whats the weather outside",
            "whats the weather like outside",
            "whats the weather like right now",
            "whats it looking like outside",
            "hows the weather outside",
            "how is the weather right now",
            "hows it look outside",
            "hows it looking outside",
            "whats the weather like at this moment",
            "what is the weather forecast",
            "whats the forecast for the day",
            "whats todays forecast",
            "what will the weather be like today",
            "whats the forecast for today",
            "whats the weather going to be like later",
            "is it going to rain later today",
            "what will the weather be like",
            "how will the weather be today",
            "what wil the weather be like later",
            "give me the weather for today",
            "show me the weather for the day",
            "can i have the weather",
            "show me the weather",
            "tell me the weather",
            "give me the weather",
            "can i get the weather",
            "can you get me the weather"
        ]
    },
    {
        "action": "sky_conditions",
        "patterns": [
            "is it cloudy right now",
            "is it overcast",
            "is it sunny outside",
            "is it raining outside",
            "what are the skies looking like",
            "how is the sky looking",
            "what do the skies look like",
            "how are the skies right now",
            "whats the sky like outside",
            "whats the sky look like right now",
            "how do the skies look",
            "what is the sky forecast",
            "is it going to rain",
            "is it gonna be nice",
            "is it going to be overcast",
            "what will the skies be like",
            "what will the skies be like today",
            "will it be overcast later",
            "whats the forecast for the sky today",
            "whats the sky look like today",
            "will it clear up later",
            "are the skies expected to clear",
            "how will the skies be today"
        ]
    },
    {
        "action": "humidity",
        "patterns": [
            "what is the air like",
            "what are the air conditions",
            "is it humid right now",
            "is it humid outside",
            "is it muggy",
            "is it muggy outside",
            "is is looking muggy",
            "is it dry",
            "is it dry outside",
            "is it looking dry outside",
            "give me the air conditions",
            "give me the humidity",
            "whats the humidity right now",
            "what is the humidity",
            "what is the humidity forecast",
            "will it be dry today",
            "what will the air be like today",
            "will it be humid later",
            "is it going to be muggy later",
            "is it going to be humid today",
            "is today going to be humid",
            "how dry will it be today",
            "how humid is it outside",
            "how muggy is it right now",
            "whats the forecast for humidity today"
        ]
    },
    {
        "action": "temperature",
        "patterns": [
            "whats the temperature outside",
            "whats the temp",
            "whats the temperature right now",
            "what is the temperature",
            "how hot is it right now",
            "how cold is it",
            "is it hot",
            "is it cold",
            "hows the temp",
            "hows the temperature",
            "is it cold outside",
            "is it hot outside",
            "whats the heat",
            "how hot is it outside",
            "how cold is it right now",
            "what is the temperature forecast",
            "is it hot today",
            "will it be hot today",
            "what will the temperature be like today",
            "will it be hot later",
            "is it going to warm up",
            "is it going to be hot today",
            "is it gonna be cold today",
            "how cold will it be today",
            "how hot will it be today",
            "hows the temp today",
            "whats the temperature today",
            "whats the forecast for temperature today"
        ]
    }
]


def build_skill(skill_config: typing.Dict, ova: "OpenVoiceAssistant"):
    from .open_weather_map import OpenWeatherMap
    return OpenWeatherMap(skill_config, ova)

def manifest():
    return {
        "name": "Open Weather Map",
        "id": "open_weather_map",
        "category": "weather",
        "required_integrations": ["open_weather_map"]
    }
