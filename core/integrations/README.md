# Integrations
* Home Assistant
* Open Weather Map

# Writing a Custom Integration
Integrations are designed as python modules that are imported by the Integration Manager. The main purpose of integrations is to augment an api that needs to be used my multiple integrations and consolidating the configuration for the api to a single module.

Integrations are located in [core/integrations](../integrations). Take a look at the available integrations. The file structure is as follows:
```
- <integration>
    - __init__.py
    - <integration>.py
```

We will use a fake integration as an example to explain the class structure.

## __init__.py
```python
import typing

def build_integration(integration_config: typing.Dict, ova: "OpenVoiceAssistant"):
    from .example_integration import ExampleIntegration
    return ExampleIntegration(integration_config, ova)

def manifest():
    return {
        "name": "Example integration",
        "id": "example_integration",
        "category": "example",
        "requirements": ["requests==2.31.0"]
        "config": {
            "host": "",
            "port": 5000,
            "api_key": ""
        }
    }
```

### build_integration

```build_integration``` function simple returns an instance of the Integration class.

### manifest

```manifest``` contains the contains information about the integration. There are 3 required fields for any integration ```name```, ```id``` and ```category```. 

```name``` is a friendly display name for the integration.<br>
```id``` should be the name of the actual integration file.<br>
```category``` describes what the integration does generaly (this is used to indicate overlapping integrations).

There are a few more fields that are not required unless your integration requires them ```requirements``` and ```config```. 

```requirements``` is a list of pip packages that are required for your integration to operate. Ex. our integration requires ```"requests==2.31.0"```. If you require multiple pip packages they must be comma separated.<br>
```config``` is a dictionary that will be imported into the integration as ```integration_config```. In this example, our integration has a config for ```host```, ```port``` and ```api_key```.<br>
Within the ```config```, datatypes will be automatically recognized on the frontend for configuration. It is important to mention that if you want your integration to be configurable with a dropdown menu, you can achieve this by adding a field that appends ```_options``` to the field name. Ex:
```
"config": {
    "unit": "fahrenheit",
    "unit_options": ["fahrenheit", "celcius", "kelvin"]
}
```
The frontend will render the ```unit``` field as a dropdown the the options being ```unit_options```. This can be applied to any field of your choice.

## example_integration.py
This file is what contains the integration logic itself, the structure should look something like this:

```python
import typing
import requests

class ExampleIntegration:

    def __init__(self, integration_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova

        host = integration_config["host"]
        port = integration_config["port"]
        acccess_token = integration_config["acccess_token"]
        self.headers = {"content-type": "application/json", "Authorization": f"Bearer {acccess_token}"}
        self.api = f"http://{host}:{port}/api"

    def get_api(self):
        resp = requests.get(f"{self.api}/", headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def post_api(self, data: typing.Dict):
        return requests.post(f"{self.api}/intent/handle", headers=self.headers, json=data)
```

The Integration class takes a config dictionary and an instance of ```OpenVoiceAssistant```. You are not required to use either of these, they simply need to be imported for every integration. 

The functions implemented in the integration are meant to be used by any integrations that use the integration.

It is HIGHLY encouraged to look at other skills to see how they work when creating a custom skill.