import typing

class HASS_ShoppingList:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova
        
        self.ha_integration = self.ova.integration_manager.get_integration_module('homeassistant')

    def add_to_shopping_list(self, context: typing.Dict):
        pos_info = context["pos_info"]
        try:
            item_to_add = pos_info["MOD_OBJECT"][0] if any(pos_info["MOD_OBJECT"]) else pos_info["OBJECT"][0]
        except KeyError:
            return "Please provide an item to add to the shopping list"
        
        data = {
            "name": item_to_add
        }
        
        resp = self.ha_integration.post_services('shopping_list', 'add_item', data)
        if resp.status_code == 200:
            return f"Adding {item_to_add} to your shopping list"
        
        return f"Failed to add {item_to_add} to your shopping list"

    def remove_from_shopping_list(self, context: typing.Dict):
        pos_info = context["pos_info"]
        try:
            item_to_remove = pos_info["MOD_OBJECT"][0] if any(pos_info["MOD_OBJECT"]) else pos_info["OBJECT"][0]
        except KeyError:
            return "Please provide an item to add to the shopping list"
        
        data = {
            "name": item_to_remove
        }
        
        resp = self.ha_integration.post_services('shopping_list', 'remove_item', data)
        if resp.status_code == 200:
            return f"Removing {item_to_remove} to your shopping list"
        
        return f"Failed to remove {item_to_remove} to your shopping list"

    def read_shopping_list(self, context: typing.Dict):
        try:
            items = self.ha_integration.get_custom('shopping_list')
        except:
            return "I could not access a shopping list"
        item_names = [item["name"] for item in items]
        if any(item_names):
            last_item = item_names.pop(-1)
            if last_item:
                return f"You have {', '.join(item_names)} and {last_item} on your shopping list"
            elif last_item:
                return f"You only have {last_item} on your shopping list"
        else:
            return "You dont have anything on your shopping list"


def build_skill(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    return HASS_ShoppingList(skill_config, ova)

def default_config():
    return {
        "required_integrations": ["homeassistant"]
    }