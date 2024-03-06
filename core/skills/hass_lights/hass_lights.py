import typing

from core.utils.nlp.preprocessing import extract_numbers, find_string_match, replace_punctuation

class HASSLights:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova

        self.ha_integration = self.ova.integration_manager.get_integration_module('home_assistant')

        self.lights = self._get_lights()
        #print('Detected lights')
        print(f"Lights : {self.lights}")

    def light_on(self, context: typing.Dict):
        try:
            entity_id, light_description = self.find_light_entity_id(context)
            #print(entity_id)
        except Exception as e:
            context['response'] = str(e)
            return

        data = {
            "entity_id": entity_id
        }
        
        resp = self.ha_integration.post_services('light', 'turn_on', data)
        if resp.status_code == 200:
            if light_description:
                response = f"Turning on the {light_description} lights."
            else:
                response = ""
        else:
            response = f"Failed to turn on the {light_description} lights."
        
        context['response'] = response

    def light_off(self, context: typing.Dict):    
        try:
            entity_id, light_description = self.find_light_entity_id(context)
            #print(entity_id)
        except Exception as e:
            context['response'] = str(e)
            return

        data = {
            "entity_id": entity_id
        }
        
        resp = self.ha_integration.post_services('light', 'turn_off', data)
        if resp.status_code == 200:
            if light_description:
                response = f"Turning off the {light_description} lights."
            else:
                response = ""
        else:
            response = f"Failed to turn off the {light_description} lights."

        context['response'] = response
    
    def light_toggle(self, context: typing.Dict):
        try:
            entity_id, light_description = self.find_light_entity_id(context)
            #print(entity_id)
        except Exception as e:
            context['response'] = str(e)
            return
            

        data = {
            "entity_id": entity_id
        }

        light_state = self.ha_integration.get_states(entity_id)
        light_mode = "off" if light_state["state"] == "on" else "on"
        
        resp = self.ha_integration.post_services('light', 'toggle', data)
        if resp.status_code == 200:
            if light_description:
                response = f"Turning {light_mode} the {light_description} lights."
            else:
                response = ""
        else:
            response =  f"Failed to turn {light_mode} the {light_description} lights."

        context['response'] = response
    
    def light_brightness(self, context: typing.Dict):
        try:
            entity_id, light_description = self.find_light_entity_id(context)
            #print(entity_id)
        except Exception as e:
            context['response'] = str(e)
            return
        
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
                if light_description:
                    response = f"Setting the {light_description} lights brightness to {percent} percent."
                else:
                    response = ""
            
            response = f"Failed to set the {light_description} lights brightness."
        else:
            response = f"Please specify a brighness level."

        context['response'] = response
    
    def find_light_entity_id(self, context: typing.Dict):
        if context["sent_info"]["ROOMS"]:
            light_description = context["sent_info"]["ROOMS"][0]
            light_id = light_description
        elif context["node_area"]:
            light_id = context["node_area"]
            light_description = ""

        if not light_id:
            raise RuntimeError("No light specified.")

        light_id = find_string_match(light_id, self.lights)
        if not light_id:
            raise RuntimeError("Could not find the light specified.")

        return light_id, light_description
    
    def _get_lights(self):
        try:
            entities = self.ha_integration.get_states()
            return [entity["entity_id"] for entity in entities if "light" in entity["entity_id"].split('.')[0]]
        except:
            return []