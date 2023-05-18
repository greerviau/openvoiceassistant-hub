# Skills
* Greetings
* Date and Time
* Home Assistant
    * Light Control
    * Shopping List
* Jokes
* Math
* Timer
* Weather

# Writing a Custom Skill
Skills are designed as python modules that are imported on the backend by the Skillset component.

Skills are located in backend/skills and have a file structure like below:
```
- <skill>
    - __init__.py
    - intents.json
    - <skill>.py
```

We will use the jokes skill as an example. So ```<skill>.py``` would be ```jokes.py```.

## __init__.py
Here we need some imports for scope.
```python
from .jokes import Jokes, build_skill, default_config
```

## intents.json
This file contains a list of intents with associated phrases. This is used to train the understanding component.
```json
{
    "intentions": [
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
}
```

You can add as many patterns as you want, and as many different actions/pattern pairs as you want. To add a new action, create a new json of action/pattern and add it to the list of ```intentions```.

## jokes.py
This file is what contains the skill logic itself, the structure should look something like this:

```python
from typing import Dict
import pyjokes

from backend import config

class Jokes:

    def __init__(self, config: Dict, ova: 'OpenVoiceAssistant'):
        self.config = config

    def tell_joke(self, config: Dict):
        return pyjokes.get_joke()


def build_skill(config: Dict, ova: 'OpenVoiceAssistant'):
    return Jokes(config, ova)

def default_config():
    return {}
```

There are 3 main pieces, the Skill class, the build_skill function and the default_config function.

The Skill class takes a config dictionary and an instance of OpenVoiceAssistant. You are not required to use either of these, they simply need to be imported for every skill. 

The only required functions are whatever actions you have in your ```intents.json``` file. The name of the functions must match the actions.

The action functions can perform any actions auxilary actions you want.

The action functions themselves must return a string response that you want to send to the user.

```build_skill``` function simple returns an instance of the Skill class.

```default_config``` contains the default configuration you want for the skill when first imported. You can then change this configuration from the UI once the skill has been imported.