import typing

from core.utils.nlp.formatting import format_readable_list

class HASSShoppingList:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova
        
        self.ha_integration = self.ova.integration_manager.get_integration_module('home_assistant')

    def add_to_shopping_list(self, context: typing.Dict):
        sent_info = context["sent_info"]
        try:
            item_to_add = sent_info["OBJECTS"][0]
        except KeyError:
            context['response'] = "Please provide an item to add to the shopping list"
            return
        
        data = {
            "name": item_to_add
        }
        
        resp = self.ha_integration.post_services('shopping_list', 'add_item', data)
        if resp.status_code == 200:
            response = f"Adding {item_to_add} to your shopping list"
        else:
            response = f"Failed to add {item_to_add} to your shopping list"

        context['response'] = response

    def remove_from_shopping_list(self, context: typing.Dict):
        sent_info = context["sent_info"]
        try:
            item_to_remove = sent_info["OBJECTS"][0]
        except KeyError:
            context['response'] = "Please provide an item to remove from the shopping list"
            return
        
        data = {
            "name": item_to_remove
        }
        
        resp = self.ha_integration.post_services('shopping_list', 'remove_item', data)
        if resp.status_code == 200:
            response = f"Removing {item_to_remove} from your shopping list"
        else:
            response = f"Failed to remove {item_to_remove} from your shopping list"

        context['response'] = response

    def read_shopping_list(self, context: typing.Dict):
        try:
            items = self.ha_integration.get_custom('shopping_list')
        except:
            context['response'] = "I could not access a shopping list"
            return
            
        item_names = [item["name"] for item in items]
        if any(item_names):
            readable_list = format_readable_list(item_names)
            response = f"You have {readable_list} on your shopping list"
        else:
            response = "You dont have anything on your shopping list"

        context['response'] = response