# Skills
* Default
    * Date / Time
    * Timer
* Home Assistant
    * Light Control
    * Shopping List
    * Vacuum
* Jokes
* Mathparse
* Open Weather Map

# Writing a Custom Skill
Skills are designed as python modules that are imported on the backend by the Skill Manager.

Skills are located in backend/skills and have a file structure like below:
```
- <skill>
    - __init__.py
    - <skill>.py
```

We will use the jokes skill as an example. So ```<skill>.py``` would be ```jokes.py```.

## \_\_init\_\_.py
Here we need some imports for scope.
```python
from .jokes import Jokes, build_skill, default_config

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

## jokes.py
This file is what contains the skill logic itself, the structure should look something like this:

```python
import typing
import pyjokes

class Jokes:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova

    def tell_joke(self, context: typing.Dict):
        return pyjokes.get_joke()


def build_skill(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    return Jokes(skill_config, ova)

def default_config():
    return {
        "name": "Jokes",
        "required_integrations": []
    }
```

There are 3 main pieces, the Skill class, the ```build_skill``` function and the ```default_config``` function.

The Skill class takes a config dictionary and an instance of ```OpenVoiceAssistant```. You are not required to use either of these, they simply need to be imported for every skill. 

The only required functions are whatever actions you have in your ```INTENTIONS``` list in the ```__init__.py``` file. The name of the functions MUST match the actions.

The action functions can perform any actions auxilary actions you want. You can utilize any integrations that you have imported. You can access an integration via the integration manager ```OpenVoiceAssistant.integration_manager.get_integration_module("<integration>")```.

The action functions themselves take a dictionary ```context``` as a parameter and must return a string response that you want to send to the user.

```build_skill``` function simple returns an instance of the Skill class.

```default_config``` contains the default configuration you want for the skill when first imported. The only required fields here are ```name``` which is a friendly name to display, and ```required_integrations``` which is a list of integrations that this skill requires. You can then change this configuration from the UI once the skill has been imported.