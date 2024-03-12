import typing

from core.utils.nlp.formatting import format_readable_list

class HASSPeople:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova
        
        self.ha_integration = self.ova.integration_manager.get_integration_module('home_assistant')

    def whos_home(self, context: typing.Dict):
        people = self._get_people()

        people_home = [person for person, state in people if state == "home"]

        if len(people_home):
            response = f"{format_readable_list(people_home)} are home."
        else:
            response = "Nobody is home."

        context['response'] = response

    def where_is_person(self, context: typing.Dict):
        command = context['cleaned_command']
        people = self._get_people()

        locations = []
        for person, state in people:
            if any(x in command.split() for x in [person, 'everyone']):
                locations.append(f"{person} is at {state}.")
        if len(locations):
            context['response'] = ' '.join(locations)
        else:
            context['response'] = "I could not find the person you're looking for."

    def _get_people(self):
        entities = self.ha_integration.get_states()
        return [(entity["entity_id"].split('.')[1], entity["state"]) for entity in entities if "person" in entity["entity_id"].split('.')[0]]