from typing import Dict
import requests

from backend import config

class HALights:

    def __init__(self, config: Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova
        self.config = config
        self.ha_integration = self.ova.integration_manager.get_integration_module('homeassistant')

        self.lights = self.get_lights()

    def light_on(self, context: Dict):
        pos_info = context["pos_info"]

        entity_id = self.get_light_id(pos_info)
        print(entity_id)

        data = {
            "entity_id": entity_id
        }
        
        light_description = pos_info["NOUN_CHUNKS"][0]
        
        resp = self.ha_integration.post_services('light', 'turn_on', data)
        if resp.status_code == 200:
            return f"Turning on {light_description}"
        
        return f"Failed to turn on {light_description}"

    def light_off(self, context: Dict):    
        pos_info = context["pos_info"]

        entity_id = self.get_light_id(pos_info)
        print(entity_id)

        data = {
            "entity_id": entity_id
        }
        
        light_description = pos_info["NOUN_CHUNKS"][0]
        
        resp = self.ha_integration.post_services('light', 'turn_off', data)
        if resp.status_code == 200:
            return f"Turning off {light_description}"
        
        return f"Failed to turn off {light_description}"
    
    def get_light_id(self, pos_info):
        try:
            light = pos_info["COMP"][0]
        except:
            return "Please provide a light to turn on"

        try:
            light_id = [l for l in self.lights if light in l][0]
        except:
            raise RuntimeError("Could not find the light specified")

        return light_id
    
    def get_lights(self):
        try:
            entities = self.ha_integration.get_states()
            return [entity["entity_id"] for entity in entities if "light" in entity["entity_id"]]
        except:
            raise RuntimeError("Failed to get list of light entites")

def build_skill(config: Dict, ova: 'OpenVoiceAssistant'):
    return HALights(config, ova)

def default_config():
    return {
        "name": "Home Assistant Lights"
    }