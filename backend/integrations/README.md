# Integrations
* Home Assistant

# Writing a Custom Integration
Integrations are designed as python modules that are imported on the backend by the Integration Manager. The main purpose of integrations is to augment an api that needs to be used my multiple skills and consolidating the configuration for the api to a single module.

Integrations are located in [backend/integrations](https://github.com/greerviau/openvoiceassistant-hub/tree/develop/backend/integrations). Take a look at the available integrations.

We will use a fake integration as an example to explain the class structure.

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


def build_integration(integration_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    return ExampleIntegration(integration_config, ova)

def default_config():
    return {
        "host": "",
        "port": 0,
        "access_token": ""
    }
```

There are 3 main pieces, the Integration class, the ```build_integration``` function and the ```default_config``` function.

The Integration class takes a config dictionary and an instance of ```OpenVoiceAssistant```. You are not required to use either of these, they simply need to be imported for every integration. 

The functions implemented in the integration are meant to be used by any skills that use the integration.

```build_integration``` function simple returns an instance of the Integration class.

```default_config``` contains the default configuration you want for the integration when first imported. You can then change this configuration from the UI once the integration has been imported.