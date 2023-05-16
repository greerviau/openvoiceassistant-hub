from typing import Dict
import requests

from backend import config

class ShoppingList:

    def __init__(self, config: Dict, ova: 'OpenVoiceAssistant'):
        self.config = config
        host = config["host"]
        acccess_token = config["acccess_token"]
        self.headers = {"content-type": "application/json", "Authorization": f"Bearer {acccess_token}"}
        self.shopping_list_api = f"http://{host}:8123/api/shopping_list"

    def add_to_shopping_list(self, config: Dict):
        return "Not implemented"

    def remove_from_shopping_list(self, config: Dict):
        return "Not implemented"

    def read_shopping_list(self, config: Dict):
        resp = requests.get(self.shopping_list_api, headers=self.headerse)
        if resp.status_code == 200:
            items = resp.json()
            item_names = [item["name"] for item in items]
            response = f"You have {', '.join(item_names)} on your shopping list"
            return response
        return "I could not access a shopping list"


def build_skill(config: Dict, ova: 'OpenVoiceAssistant'):
    return ShoppingList(config, ova)

def default_config():
    return {}