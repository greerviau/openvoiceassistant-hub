import typing

class HASS_ShoppingList:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova
        
        self.ha_integration = self.ova.integration_manager.get_integration_module('home_assistant')

    def add_to_shopping_list(self, context: typing.Dict):
        pos_info = context["pos_info"]
        try:
            item_to_add = pos_info["MOD_OBJECT"][0] if any(pos_info["MOD_OBJECT"]) else pos_info["OBJECT"][0]
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
        pos_info = context["pos_info"]
        try:
            item_to_remove = pos_info["MOD_OBJECT"][0] if any(pos_info["MOD_OBJECT"]) else pos_info["OBJECT"][0]
        except KeyError:
            context['response'] = "Please provide an item to remove from the shopping list"
            return
        
        data = {
            "name": item_to_remove
        }
        
        resp = self.ha_integration.post_services('shopping_list', 'remove_item', data)
        if resp.status_code == 200:
            response = f"Removing {item_to_remove} to your shopping list"
        else:
            response = f"Failed to remove {item_to_remove} to your shopping list"

        context['response'] = response

    def read_shopping_list(self, context: typing.Dict):
        try:
            items = self.ha_integration.get_custom('shopping_list')
        except:
            context['response'] = "I could not access a shopping list"
            return
            
        item_names = [item["name"] for item in items]
        if any(item_names):
            last_item = item_names.pop(-1)
            if last_item:
                response = f"You have {', '.join(item_names)} and {last_item} on your shopping list"
            elif last_item:
                response = f"You only have {last_item} on your shopping list"
        else:
            response = "You dont have anything on your shopping list"

        context['response'] = response

def build_skill(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    return HASS_ShoppingList(skill_config, ova)

def default_config():
    return {
        "required_integrations": ["home_assistant"]
    }