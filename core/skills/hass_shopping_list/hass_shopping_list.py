import typing
import logging
logger = logging.getLogger("skill.hass_shopping_list")

from core.utils.nlp.formatting import format_readable_list

class HASSShoppingList:

    def __init__(self, skill_config: typing.Dict, ova: "OpenVoiceAssistant"):
        self.ova = ova
        
        self.ha_integration = self.ova.integration_manager.get_integration_module("home_assistant")

    def add_to_shopping_list(self, context: typing.Dict):
        sent_info = context["sent_info"]
        items = sent_info["ITEMS"]
        if any(items):
            for item in items:
                data = {
                    "name": item
                }
                
                resp = self.ha_integration.post_services("shopping_list", "add_item", data)
                if resp.status_code != 200:
                    context["response"] = f"Failed to add {item} to your shopping list"
                    return
                    
            items_readable_list = format_readable_list(items)
            context["response"] = f"Adding {items_readable_list} to your shopping list"
        else:
            context["response"] = "Please provide an item to add to the shopping list"

    def remove_from_shopping_list(self, context: typing.Dict):
        sent_info = context["sent_info"]
        items = sent_info["ITEMS"]
        if any(items):
            for item in items:
                data = {
                    "name": item
                }
                
                resp = self.ha_integration.post_services("shopping_list", "remove_item", data)
                if resp.status_code != 200:
                    context["response"] = f"Failed to remove {item} from your shopping list"
                    return
                    
            items_readable_list = format_readable_list(items)
            context["response"] = f"Removing {items_readable_list} from your shopping list"
        else:
            context["response"] = "Please provide an item to remove from the shopping list"

    def read_shopping_list(self, context: typing.Dict):
        try:
            items = self.ha_integration.get_custom("shopping_list")
        except:
            context["response"] = "I could not access a shopping list"
            return
            
        item_names = [item["name"] for item in items]
        if any(item_names):
            readable_list = format_readable_list(item_names)
            response = f"You have {readable_list} on your shopping list"
        else:
            response = "You dont have anything on your shopping list"

        context["response"] = response