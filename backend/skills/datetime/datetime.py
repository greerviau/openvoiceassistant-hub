from typing import Dict
from datetime import datetime
import pytz

class Datetime:
    def __init__(self, config: Dict):
        self.config = config
        self.tz = pytz.timezone(config["timezone"])
        self.format = "%H" if config["24_hour_format"] else "%I"

    def date(self, context: Dict):
        date = datetime.now(self.tz).strftime("%B %d, %Y")

        response = f"Today is {date}"

        return response

    def time(self, context: Dict):
        time = datetime.now(self.tz).strftime(f"{self.format}:%M")

        response = f"It is {time}"

        return response

    def day_of_week(self, context: Dict):
        dow = datetime.now(self.tz).strftime('%A')

        response = f"It is {dow}"

        return response

def build_skill(config: Dict):
    return Datetime(config)

def default_config():
    return {
        "timezone": "US/Eastern",
        "24_hour_format": False
    }