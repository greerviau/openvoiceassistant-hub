import typing

class HASS_Vacuum:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova
        
        self.ha_integration = self.ova.integration_manager.get_integration_module('home_assistant')

    def start_vacuum(self, context: typing.Dict):
        data = {
            "entity_id": "all"
        }
        
        resp = self.ha_integration.post_services('vacuum', 'start', data)
        if resp.status_code == 200:
            return "Starting the vacuum"
        
        return "Failed to start the vacuum"

    def pause_vacuum(self, context: typing.Dict):
        data = {
            "entity_id": "all"
        }
        
        resp = self.ha_integration.post_services('vacuum', 'stop', data)
        if resp.status_code == 200:
            return "Pausing the vacuum"
        
        return "Failed to pause the vacuum"

    def stop_vacuum(self, context: typing.Dict):
        data = {
            "entity_id": "all"
        }
        
        resp = self.ha_integration.post_services('vacuum', 'return_to_base', data)
        if resp.status_code == 200:
            return "Sending the vacuum back home"
        
        return "Failed to send the vacuum back home"

def build_skill(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    return HASS_Vacuum(skill_config, ova)

def default_config():
    return {
        "required_integrations": ["home_assistant"]
    }