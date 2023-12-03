from typing import Dict
import requests

from backend import config

class HALights:

    def __init__(self, config: Dict, ova: 'OpenVoiceAssistant'):
        self.config = config
        host = config["host"]
        acccess_token = config["acccess_token"]
        self.headers = {"content-type": "application/json", "Authorization": f"Bearer {acccess_token}"}
        self.api = f"http://{host}:8123/api"

    def light_on(self, context: Dict):
        pos_info = context["pos_info"]

        body = {
            "entity_id": self.get_light_id(pos_info)
        }
        
        light_description = pos_info["NOUN_CHUNKS"][0]
        
        resp = requests.post(f"{self.api}/services/light/turn_on", headers=self.headers, json=body)
        if resp.status_code == 200:
            return f"Turning on {light_description}"
        
        return f"Failed to turn on {light_description}"

    def light_off(self, context: Dict):    
        pos_info = context["pos_info"]

        body = {
            "entity_id": self.get_light_id(pos_info)
        }
        
        light_description = pos_info["NOUN_CHUNKS"][0]
        
        resp = requests.post(f"{self.api}/services/light/turn_off", headers=self.headers, json=body)
        if resp.status_code == 200:
            return f"Turning off {light_description}"
        
        return f"Failed to turn off {light_description}"
    
    def get_light_id(self, pos_info):
        try:
            light = pos_info["COMP"][0]
        except:
            return "Please provide a light to turn on"
        
        lights = self.get_lights()

        try:
            light_id = [l for l in lights if light in l][0]
        except:
            raise RuntimeError("Could not find the light specified")

        return light_id
    
    def get_lights(self):
        resp = requests.get(f"{self.api}/states", headers=self.headers)
        if resp.status_code == 200:
            entities = resp.json()
            return [entity["entity_id"] for entity in entities if "light" in entity["entity_id"]]
        raise RuntimeError("Failed to get list of light entites")

def build_skill(config: Dict, ova: 'OpenVoiceAssistant'):
    return HALights(config, ova)

def default_config():
    return {
        "name": "Home Assistant Lights"
    }