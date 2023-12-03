from typing import Dict
import requests

from backend import config

class HAShoppingList:

    def __init__(self, config: Dict, ova: 'OpenVoiceAssistant'):
        self.config = config
        host = config["host"]
        acccess_token = config["acccess_token"]
        self.headers = {"content-type": "application/json", "Authorization": f"Bearer {acccess_token}"}
        self.api = f"http://{host}:8123/api"

    def add_to_shopping_list(self, context: Dict):
        pos_info = context["pos_info"]
        try:
            item_to_add = pos_info["MOD_OBJECT"] if "MOD_OBJECT" in pos_info else pos_info["OBJECT"][0]
        except KeyError:
            return "Please provide an item to add to the shopping list"
        
        body = {
            "name": item_to_add
        }
        
        resp = requests.post(f"{self.api}/services/shopping_list/add_item", headers=self.headers, json=body)
        if resp.status_code == 200:
            return f"Adding {item_to_add} to your shopping list"
        
        return f"Failed to add {item_to_add} to your shopping list"

    def remove_from_shopping_list(self, context: Dict):
        pos_info = context["pos_info"]
        try:
            item_to_remove = pos_info["MOD_OBJECT"] if "MOD_OBJECT" in pos_info else pos_info["OBJECT"][0]
        except KeyError:
            return "Please provide an item to add to the shopping list"
        
        body = {
            "name": item_to_remove
        }
        
        resp = requests.post(f"{self.api}/services/shopping_list/remove_item", headers=self.headers, json=body)
        if resp.status_code == 200:
            return f"Removing {item_to_remove} to your shopping list"
        
        return f"Failed to remove {item_to_remove} to your shopping list"

    def read_shopping_list(self, context: Dict):
        resp = requests.get(f"{self.api}/shopping_list", headers=self.headers)
        if resp.status_code == 200:
            items = resp.json()
            item_names = [item["name"] for item in items]
            if any(item_names):
                last_item = item_names.pop(-1)
                if last_item:
                    return f"You have {', '.join(item_names)} and {last_item} on your shopping list"
                elif last_item:
                    return f"You only have {last_item} on your shopping list"
            else:
                return "You dont have anything on your shopping list"
        return "I could not access a shopping list"


def build_skill(config: Dict, ova: 'OpenVoiceAssistant'):
    return HAShoppingList(config, ova)

def default_config():
    return {
        "name": "Home Assistant Shopping List"
    }