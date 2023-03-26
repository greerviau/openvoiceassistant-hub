from typing import Dict
from datetime import datetime

class Datetime:
    def __init__(self, config: Dict):
        self.config = config

    def date(self, context: Dict):
        date = datetime.now().strftime("%B %d, %Y")

        response = f"Today is {date}"

        return response

    def time(self, context: Dict):
        time = datetime.now().strftime("%H:%M")

        response = f"It is {time}"

        return response

    def day_of_week(self, context: Dict):
        dow = datetime.now().strftime('%A')

        response = f"It is {dow}"

        return response

def build_skill(config: Dict):
    return Datetime(config)

def default_config():
    return {}