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
            if person in command.split():
                locations.append(f"{person} is at {state}.")

        context['response'] = ' '.join(locations)

    def _get_people(self):
        return [entity["entity_id"].split('.')[1], entity["state"] for entity in entities if "person" in entity["entity_id"].split('.')[0]]