# Skills
* Default
    * Volume Control
    * Date / Time
    * Timer
* Home Assistant
    * Light Control
    * Shopping List
    * Vacuum
* PyJokes
* Mathparse
* Open Weather Map

# Writing a Custom Skill
Skills are designed as python modules that are imported on the backend by the Skill Manager.

Integrations are located in [backend/skills](https://github.com/greerviau/openvoiceassistant-hub/tree/develop/backend/skills). Take a look at the available integrations. The file structure is as follows:
```
- <skill>
    - __init__.py
    - <skill>.py
```

We will use the PyJokes skill as an example. So ```<skill>.py``` would be ```pyjokes.py```.

## \_\_init\_\_.py
Here we need some imports for scope.
```python
from .pyJokes import PyJokes, build_skill, default_config

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
```

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

## pyjokes.py
This file is what contains the skill logic itself, the structure should look something like this:

```python
import typing
import pyjokes

class PyJokes:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova

    def tell_joke(self, context: typing.Dict):
        return pyjokes.get_joke()


def build_skill(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    return Jokes(skill_config, ova)

def default_config():
    return {}
```

There are 3 main pieces, the Skill class, the ```build_skill``` function and the ```default_config``` function.

The Skill class takes a config dictionary and an instance of ```OpenVoiceAssistant```. You are not required to use either of these, they simply need to be imported for every skill. 

The only required functions are whatever actions you have in your ```INTENTIONS``` list in the ```__init__.py``` file. The name of the functions MUST match the actions.

The action functions can perform any actions auxilary actions you want. You can utilize any integrations that you have imported. You can access an integration via the integration manager ```OpenVoiceAssistant.integration_manager.get_integration_module("<integration>")```.

The action functions themselves take a dictionary ```context``` as a parameter and must return a string response that you want to send to the user.

```build_skill``` function simple returns an instance of the Skill class.

```default_config``` contains the default configuration you want for the skill when first imported. There are no required fields, only what is necessary to configure your skill. You can then change this configuration from the UI once the skill has been imported.

If you are writing a skill that uses an integration, then it is required to add a field to your configuration called ```required_integrations```. For example if you are making a Home Assistant based skill, and want to utilize the Home Assistant integration, you need the following for your ```default_config```:

```python
def default_config():
    return {
        "required_integrations": ["home_assistant"]
    }
```

You can use as many integrations in a skill as necessary, but you must insert the integration name into the ```required_integrations``` list.