import typing

from backend.utils.nlp import extract_numbers

class HASS_Lights:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova

        self.ha_integration = self.ova.integration_manager.get_integration_module('homeassistant')

        self.lights = self.get_lights()
        #print('Detected lights')
        #print(self.lights)

    def light_on(self, context: typing.Dict):
        try:
            entity_id, light_description = self.find_light_entity_id(context)
            #print(entity_id)
        except:
            return "No light specified"

        data = {
            "entity_id": entity_id
        }
        
        resp = self.ha_integration.post_services('light', 'turn_on', data)
        if resp.status_code == 200:
            if not light_description:
                return f"Turning on {light_description}"
            else:
                return ""
        
        return f"Failed to turn on {light_description}"

    def light_off(self, context: typing.Dict):    
        try:
            entity_id, light_description = self.find_light_entity_id(context)
            #print(entity_id)
        except:
            return "No light specified"

        data = {
            "entity_id": entity_id
        }
        
        resp = self.ha_integration.post_services('light', 'turn_off', data)
        if resp.status_code == 200:
            if not light_description:
                return f"Turning off {light_description}"
            else:
                return ""
        
        return f"Failed to turn off {light_description}"
    
    def light_toggle(self, context: typing.Dict):
        try:
            entity_id, light_description = self.find_light_entity_id(context)
            #print(entity_id)
        except:
            return "No light specified"

        data = {
            "entity_id": entity_id
        }

        light_state = self.ha_integration.get_states(entity_id)
        light_mode = "off" if light_state["state"] == "on" else "on"
        
        resp = self.ha_integration.post_services('light', 'toggle', data)
        if resp.status_code == 200:
            if not light_description:
                return f"Turning {light_mode} {light_description}"
            else:
                return ""
        
        return f"Failed to turn {light_mode} {light_description}"
    
    def light_brightness(self, context: typing.Dict):
        try:
            entity_id, light_description = self.find_light_entity_id(context)
            #print(entity_id)
        except:
            return "No light specified"
        
        command = context['cleaned_command']
        
        if "percent" in command:
            numbers = extract_numbers(command)
            percent = int(numbers[0])

            data = {
                "entity_id": entity_id,
                "brightness_pct": percent
            }
            
            resp = self.ha_integration.post_services('light', 'turn_on', data)
            if resp.status_code == 200:
                if not light_description:
                    return f"Setting the {light_description} brightness to {percent} percent"
                else:
                    return ""
            
            return f"Failed to set the {light_description} brightness"
        else:
            return f"Please specify a brighness level"
    
    def find_light_entity_id(self, context: typing.Dict):
        try:
            light = '_'.join(context["pos_info"]["COMP"])
            light_description = context['pos_info']["NOUN_CHUNKS"][0]
        except Exception as err:
            #print(err)
            light = context["node_area"]
            #print(light)
            light_description = ""

        if not light:
            raise RuntimeError("No light specified")

        try:
            light_id = [l for l in self.lights if light in l][0]
        except:
            raise RuntimeError("Could not find the light specified")

        return light_id, light_description
    
    def get_lights(self):
        try:
            entities = self.ha_integration.get_states()
            return [entity["entity_id"] for entity in entities if "light" in entity["entity_id"].split('.')[0]]
        except:
            raise RuntimeError("Failed to get list of light entites")

def build_skill(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    return HASS_Lights(skill_config, ova)

def default_config():
    return {
        "name": "Home Assistant Lights",
        "required_integrations": ["homeassistant"]
    }