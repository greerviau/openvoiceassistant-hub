import typing

class HASS_Vacuum:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova
        
        self.ha_integration = self.ova.integration_manager.get_integration_module('homeassistant')

    def start_vacuum(self, context: typing.Dict):
        data = {
            "entity_id": "all"
        }
        
        resp = self.ha_integration.post_services('vacuum', 'start', data)
        if resp.status_code == 200:
            return f"Starting the vacuum"
        
        return f"Failed to start the vacuum"

    def stop_vacuum(self, context: typing.Dict):
        data = {
            "entity_id": "all"
        }
        
        resp = self.ha_integration.post_services('vacuum', 'stop', data)
        if resp.status_code == 200:
            return f"Stopping the vacuum"
        
        return f"Failed to stop the vacuum"

    def return_to_base(self, context: typing.Dict):
        data = {
            "entity_id": "all"
        }
        
        resp = self.ha_integration.post_services('vacuum', 'return_to_base', data)
        if resp.status_code == 200:
            return f"Sending the vacuum back home"
        
        return f"Failed to send the vacuum back home"

def build_skill(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    return HASS_Vacuum(skill_config, ova)

def default_config():
    return {
        "name": "Home Assistant Vacuum",
        "required_integrations": ["homeassistant"]
    }