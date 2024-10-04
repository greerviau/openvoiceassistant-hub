import typing
import importlib
import logging
logger = logging.getLogger("skill.recipes")

class Recipes:

    def __init__(self, skill_config: typing.Dict, ova: "OpenVoiceAssistant"):
        self.ova = ova

        source = skill_config["source"]
        logger.info(f"Using recipe source: {source}")
        self.recipe_finder = importlib.import_module(f"core.skills.recipes.{source}")
        self.current_recipe = None

    def find_recipe(self, context: typing.Dict):
        recipes = context["sent_info"]["OBJECTS"]
        if recipes:
            recipe_name = recipes[0]
            recipe_list = self.recipe_finder.fetch_recipe(recipe_name)
            if recipe_list:
                recipe = recipe_list[0]
                self.current_recipe = recipe
                recipe_title = recipe["title"]
                response = f"I found a recipe for {recipe_title}. Would you like to try it?"
                context["hub_callback"] = "recipes.read_ingredients"
            else:
                context["response"] = f"Sorry, I could not find any recipes for {recipe_name}."
        else:
            context["response"] = "Sorry, could you provide a recipe for me to find."

    def read_ingredients(self, context: typing.Dict):
        pass
