import typing

INTENTIONS = [
        {
            "action":"find_recipe",
            "patterns":[
                "give me a recipe for BLANK",
                "give me a BLANK recipe",
                "find me a recipe for BLANK",
                "find me a BLANK recipe",
                "look up a recipe for BLANK",
                "look up a BLANK recipe",
                "what are the ingredients for BLANK",
                "what ingredients are in BLANK",
                "what ingredients do i need to make BLANK",
                "read me the ingredients",
                "read the ingredients to BLANK",
                "what are the instructions to BLANK",
                "how do i make BLANK",
                "tell me how to make BLANK",
                "tell me the instructions to make BLANK",
                "how can i make BLANK"
            ]
        }
    ]

def build_skill(skill_config: typing.Dict, ova: "OpenVoiceAssistant"):
    from .recipe import Recipe
    return Recipe(skill_config, ova)

def manifest():
    return {
        "name": "Recipes",
        "id": "recipes",
        "category": "recipes",
        "config": {
            "source": "all_recipes",
            "source_options": ["all_recipes"]
        }
    }