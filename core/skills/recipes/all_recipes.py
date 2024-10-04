from typing import List, Dict
import logging
logger = logging.getLogger("skill.recipes.all_recipes")
import requests
from bs4 import BeautifulSoup

def fetch_recipe(recipe_name: str) -> List[Dict]:
    url = f"https://www.allrecipes.com/search?q={recipe_name}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        recipes = soup.find_all("a", class_="comp mntl-card-list-items mntl-document-card mntl-card card card--no-image")

    recipe_list = []
    for recipe in recipes:
        recipe_data = {}

        title = recipe.find("span", class_="card__title-text")
        recipe_data["title"] = title.text.strip()

        recipe_url = recipe["href"]
        recipe_data["url"] = recipe_url

        response = requests.get(recipe_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Extracting ingredients
            ingredients = soup.find_all("li", class_="mntl-structured-ingredients__list-item")
            recipe_data["ingredients"] = [ingredient.text.strip() for ingredient in ingredients]

            # Extracting instructions
            instructions = soup.find_all("li", class_="comp mntl-sc-block mntl-sc-block-startgroup mntl-sc-block-group--LI")
            recipe_data["instructions"] = [instruction.find("p").text.strip() for instruction in instructions]

            # Extracting video link if available
            video_link_tag = soup.find("a", class_="video-playlist-teaser__image")
            recipe_data["video"] = video_link_tag["href"] if video_link_tag else None

            recipe_list.append(recipe_data)
        else:
            logger.error("Error fetching recipe details.")
    return recipe_list