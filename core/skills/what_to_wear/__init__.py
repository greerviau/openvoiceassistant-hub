import typing

INTENTIONS = [
        {
            "action": "suggest_clothes",
            "patterns": [
                "what should i wear today",
                "what to wear today",
                "what do you think i should wear today"
                "how should i dress today",
                "how should i dress for today"
                "what should i wear based on the weather",
                "what clothes should i wear today",
                "what should i put on today"
            ]
        }
    ]

def build_skill(skill_config: typing.Dict, ova: "OpenVoiceAssistant"):
    from .what_to_wear import WhatToWear
    return WhatToWear(skill_config, ova)

def manifest():
    return {
        "name": "What to Wear",
        "id": "what_to_wear",
        "category": "weather.suggestion",
        "required_integrations": ["open_weather_map"]
    }