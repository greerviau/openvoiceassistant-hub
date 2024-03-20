import typing

INTENTIONS = [
        {
            "action":"start_vacuum",
            "patterns":[
                "start the vacuum",
                "start vacuuming",
                "clean the floor",
                "clean the house",
                "vacuum the floor",
                "vacuum the house"
            ]
        },
        {
            "action":"pause_vacuum",
            "patterns":[
                "pause the vacuum",
                "pause the vacuum",
                "pause the vacuum",
                "pause the vacuum",
                "pause the vacuum",
                "pause the vacuum",
            ]
        },
        {
            "action":"stop_vacuum",
            "patterns":[
                "stop the vacuum",
                "stop vacuuming",
                "quit vacuuming",
                "send the vacuum home",
                "stop cleaning",
                "quit cleaning"
            ]
        }
    ]

def build_skill(skill_config: typing.Dict, ova: "OpenVoiceAssistant"):
    from .hass_vacuum import HASSVacuum
    return HASSVacuum(skill_config, ova)

def manifest():
    return {
        "name": "HASS Vacuum",
        "id": "hass_vacuum",
        "category": "iot_control.vacuum",
        "required_integrations": ["home_assistant"]
    }