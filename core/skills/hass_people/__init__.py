import typing

INTENTIONS = [
        {
            "action":"whos_home",
            "patterns":[
                "whos home",
                "whos at home",
                "whos at home",
                "who is at home",
                "who is home",
                "is anyone home"
                "is anyone at home"
            ]
        },
        {
            "action":"where_is_person",
            "patterns":[
                "where is BLANK",
                "where is everyone",
                "wheres BLANK",
                "wheres everyone"
            ]
        }
    ]

def build_skill(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    from .hass_people import HASSPeople
    return HASSPeople(skill_config, ova)

def manifest():
    return {
        "name": "HASS People",
        "id": "hass_people",
        "category": "people",
        "required_integrations": ["home_assistant"],
        "condig": {
            "excluded_users": []
        }
    }