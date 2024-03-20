# Skills
* Default
    * Volume Control
    * Date / Time
    * Timer
* Home Assistant
    * Light Control
    * Shopping List
    * Vacuum
    * People
* PyJokes
* Open Weather Map
* What to Wear
* Yahoo Finance

# Writing a Custom Skill
Skills are designed as python modules that are imported by the Skill Manager.

Skills are located in [core/skills](../skills). Take a look at the available skills. The file structure is as follows:
```
- <skill>
    - __init__.py
    - <skill>.py
```

We will use the PyJokes skill as an example. So ```<skill>.py``` would be ```pyjokes.py```.

## \_\_init\_\_.py
Here we need some imports for scope.
```python
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

def build_skill(skill_config: typing.Dict, ova: "OpenVoiceAssistant"):
    from .pyjokes import PyJokes
    return PyJokes(skill_config, ova)

def manifest():
    return {
        "name": "PyJokes",
        "id": "pyjokes",
        "category": "jokes",
        "requirements": ["pyjokes==0.6.0"]
    }
```

There are 3 main pieces, the ```INTENTIONS```, the ```build_skill``` function and the ```manifest``` function.

### INTENTIONS

You can add as many patterns as you want, and as many different action/pattern pairs as you want. To add a new action, create a new json of action/pattern and add it to the list of ```INTENTIONS```.

When creating patterns for an intent, it is important to use at least 5 patterns, it is better if they are unique and cover a wide range of possible ways to express the intent. 

But if you can't find different ways to phrase what you want to say, it is also ok to duplicate patterns. This just gives the classifier more examples to pull from when training (only really important for Neural Intent classifier).

For example instead of the following:
```
{
    "action":"stop_vacuum",
    "patterns":[
        "stop the vacuum",
        "stop vacuuming"
    ]
}
```

Just duplicate the patterns to get atleast 5:
```
{
    "action":"stop_vacuum",
    "patterns":[
        "stop the vacuum",
        "stop vacuuming",
        "stop the vacuum",
        "stop vacuuming",
        "stop the vacuum",
        "stop vacuuming"
    ]
}
```

Dont go too overboard with duplication for situations like this, just enough to get at least 5 total patterns.

### build_skill

```build_skill``` function simple returns an instance of the Skill class. **You must import the skill class within this function.**

### manifest

```manifest``` contains the contains information about the skill. There are 3 required fields:<br>
```name``` is a friendly display name for the skill.<br>
```id``` should be the name of the actual skill file.<br>
```category``` describes what the skill does generaly (this is used to indicate overlapping skills).

There are a few more fields that are not required unless your skill requires them:<br>
```requirements``` is a list of pip packages that are required for your skill to operate. Ex. pyjoes requires ```pyjokes==0.6.0```. If you require multiple pip packages they must be comma separated.<br>
```config``` is a dictionary that will be imported into the skill as ```skill_config```. Ex. Yahoo Finance has a ```config```<br>
```
"config": {
    "watch_list": [
        "^GSPC",
        "VTI",
        "BND"
    ]
}
```
Within the ```config```, datatypes will be automatically recognized on the frontend for configuration. It is important to mention that if you want your skill to be configurable with a dropdown menu, you can achieve this by adding a field that appends ```_options``` to the field name. Ex.
```
"config": {
    "unit": "fahrenheit",
    "unit_options": ["fahrenheit", "celcius", "kelvin"]
}
```
The frontend will render the ```unit``` field as a dropdown the the options being ```unit_options```. This can be applied to any field of your choice.<br>
```required_integrations``` is a list of the required integrations that the skill needs to operate. If you require multiple integrations they must be comma seperated.

## pyjokes.py
This file is what contains the skill logic itself, the structure should look something like this:

```python
import typing
import pyjokes
import logging
logger = logging.getLogger("skill.pyjokes")

class PyJokes:

    def __init__(self, skill_config: typing.Dict, ova: "OpenVoiceAssistant"):
        self.ova = ova

    def tell_joke(self, context: typing.Dict):
        context["response"] = pyjokes.get_joke()
```

The Skill class takes a config dictionary and an instance of ```OpenVoiceAssistant```. You are not required to use either of these, they simply need to be imported for every skill. 

The only required functions are whatever actions you have in your ```INTENTIONS``` list in the ```__init__.py``` file. The name of the functions MUST match the actions.

The action functions can perform any actions auxilary actions you want. You can utilize any integrations that you have imported. You can access an integration via the integration manager ```OpenVoiceAssistant.integration_manager.get_integration_module("<integration>")```.

The action functions themselves take a dictionary ```context``` as a parameter. The function must ultimately set the ```response``` field in the context dictionary with the response to provide to the user. If no response is set, then the assistant will not audibly respond (sometimes this is desired). You can also set the ```synth_response``` if you need to format your response with a text formatting that would be easier for the TTS engine to synthesize (see default/time for example).

It is HIGHLY encouraged to look at other skills to see how they work when creating a custom skill.