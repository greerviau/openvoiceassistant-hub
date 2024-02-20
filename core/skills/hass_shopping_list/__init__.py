import typing

INTENTIONS = [
        {
            "action":"add_to_shopping_list",
            "patterns":[
                "add BLANK to my shopping list",
                "add BLANK to my grocery list",
                "add BLANK to the shopping list",
                "add BLANK to the grocery list",
                "put BLANK on the shopping list"
                "put BLANK on the grocery list"
            ]
        },
        {
            "action":"remove_from_shopping_list",
            "patterns":[
                "remove BLANK from my shopping list",
                "remove BLANK from my grocery list",
                "remove BLANK from the shopping list",
                "remove BLANK from the grocery list",
                "take BLANK off the shopping list",
                "take BLANK off the grocery list"
            ]
        },
        {
            "action":"read_shopping_list",
            "patterns":[
                "whats on my shopping list",
                "whats on the shopping list",
                "whats on the grocery list",
                "what do i have on my shopping list",
                "what do i have on the shopping list",
                "what do i have on my grocery list",
                "what do i have on the grocery list",
                "read my shopping list",
                "read whats on my shopping list",
                "show my shopping list",
                "show me wahts on my shopping list"
            ]
        }
    ]

def build_skill(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    from .hass_shopping_list import HASSShoppingList
    return HASSShoppingList(skill_config, ova)

def manifest():
    return {
        "name": "HASS Shopping List",
        "id": "hass_shopping_list",
        "category": "shopping_list",
        "required_integrations": ["home_assistant"]
    }