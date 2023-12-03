from typing import Dict
import requests

from backend import config

class HAVacuum:

    def __init__(self, config: Dict, ova: 'OpenVoiceAssistant'):
        self.config = config
        self.ha_integration = self.ova.integration_manager.get_integration_module('homeassistant')

    def start_vacuum(self, context: Dict):
        data = {
            "entity_id": "all"
        }
        
        resp = self.ha_integration.post_services('vacuum', 'start', data)
        if resp.status_code == 200:
            return f"Starting the vacuum"
        
        return f"Failed to start the vacuum"

    def stop_vacuum(self, context: Dict):
        data = {
            "entity_id": "all"
        }
        
        resp = self.ha_integration.post_services('vacuum', 'stop', data)
        if resp.status_code == 200:
            return f"Stopping the vacuum"
        
        return f"Failed to stop the vacuum"

    def return_to_base(self, context: Dict):
        data = {
            "entity_id": "all"
        }
        
        resp = self.ha_integration.post_services('vacuum', 'return_to_base', data)
        if resp.status_code == 200:
            return f"Sending the vacuum back home"
        
        return f"Failed to send the vacuum back home"

def build_skill(config: Dict, ova: 'OpenVoiceAssistant'):
    return HAVacuum(config, ova)

def default_config():
    return {
        "name": "Home Assistant Vacuum"
    }