import typing

def build_integration(integration_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    from .home_assistant import HomeAssistant
    return HomeAssistant(integration_config, ova)

def manifest():
    return {
        "name": "Home Assistant",
        "id": "home_assistant",
        "category": "smart_home",
        "requirements": ["requests==2.31.0"],
        "config": {
            "host": "",
            "port": 8123,
            "acccess_token": ""
        }
    }