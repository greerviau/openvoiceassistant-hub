from typing import Dict
import requests

from backend import config

class Vacuum:

    def __init__(self, config: Dict, ova: 'OpenVoiceAssistant'):
        self.config = config
        host = config["host"]
        acccess_token = config["acccess_token"]
        self.headers = {"content-type": "application/json", "Authorization": f"Bearer {acccess_token}"}
        self.api = f"http://{host}:8123/api"

    def start_vacuum(self, context: Dict):
        body = {
            "entity_id": "all"
        }
        
        resp = requests.post(f"{self.api}/services/vacuum/start", headers=self.headers, json=body)
        if resp.status_code == 200:
            return f"Starting the vacuum"
        
        return f"Failed to start the vacuum"

    def stop_vacuum(self, context: Dict):
        body = {
            "entity_id": "all"
        }
        
        resp = requests.post(f"{self.api}/services/vacuum/stop", headers=self.headers, json=body)
        if resp.status_code == 200:
            return f"Stopping the vacuum"
        
        return f"Failed to stop the vacuum"

    def return_to_base(self, context: Dict):
        body = {
            "entity_id": "all"
        }
        
        resp = requests.post(f"{self.api}/services/vacuum/return_to_base", headers=self.headers, json=body)
        if resp.status_code == 200:
            return f"Sending the vacuum back home"
        
        return f"Failed to send the vacuum back home"

def build_skill(config: Dict, ova: 'OpenVoiceAssistant'):
    return Vacuum(config, ova)

def default_config():
    return {}