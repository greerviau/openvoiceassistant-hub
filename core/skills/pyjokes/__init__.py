import typing

INTENTIONS = [
        {
            "action":"tell_joke",
            "patterns":[
                "tell me a joke",
                "make me laugh",
                "can you make me laugh",
                "can you tell me a joke",
                "tell me a funny joke",
                "can you tell me a funny joke",
                "make a funny joke",
                "make a joke"
            ]
        }
    ]

def build_skill(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    from .pyjokes import PyJokes
    return PyJokes(skill_config, ova)

def manifest():
    return {
        "name": "PyJokes",
        "id": "pyjokes",
        "category": "jokes",
        "requirements": ["pyjokes==0.6.0"]
    }