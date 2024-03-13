import typing
import logging
logger = logging.getLogger("skill.hass_vacuum")

class HASSVacuum:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova
        
        self.ha_integration = self.ova.integration_manager.get_integration_module('home_assistant')

    def start_vacuum(self, context: typing.Dict):
        data = {
            "entity_id": "all"
        }
        
        resp = self.ha_integration.post_services('vacuum', 'start', data)
        if resp.status_code == 200:
            response = "Starting the vacuum"
        else:
            response = "Failed to start the vacuum"

        context['response'] = response

    def pause_vacuum(self, context: typing.Dict):
        data = {
            "entity_id": "all"
        }
        
        resp = self.ha_integration.post_services('vacuum', 'stop', data)
        if resp.status_code == 200:
            response = "Pausing the vacuum"
        else:
            response = "Failed to pause the vacuum"

        context['response'] = response

    def stop_vacuum(self, context: typing.Dict):
        data = {
            "entity_id": "all"
        }
        
        resp = self.ha_integration.post_services('vacuum', 'return_to_base', data)
        if resp.status_code == 200:
            response = "Sending the vacuum back home"
        else:
            response = "Failed to send the vacuum back home"

        context['response'] = response