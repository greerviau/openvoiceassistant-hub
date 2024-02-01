import typing
from datetime import datetime
import pytz

from backend.utils.nlp import extract_numbers
from backend.utils.formatting import format_readable_date, format_readable_time

class Default:

    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova

        self.tz = pytz.timezone(skill_config["timezone"])
        self.hour_format = "%H" if skill_config["24_hour_format"] else "%I"

    def introduction(self, context: typing.Dict):
        return "Hello, my name is ova. I am an opensource voice assistant designed to be a locally controlled alternative to popular voice assistants on the market like Alexa, and Google home."

    def volume(self, context: typing.Dict):
        node_id = context["node_id"]
        command = context['cleaned_command']

        numbers = extract_numbers(command)
        value = int(numbers[0])

        if 'percent' in command or value > 10:
            response = f"Setting the volume to {value} percent"
            volume_percent = value
        else:
            response = f"Setting the volume to {value}"
            volume_percent = value * 10

        node_config = self.ova.node_manager.get_node_config(node_id)
        node_config["volume"] = volume_percent
        self.ova.node_manager.update_node_config(node_id, node_config)

        self.ova.node_manager.call_node_api("PUT", node_id, "/set_volume", data={"volume_percent": volume_percent})
        return response
    
    def date(self, context: typing.Dict):
        date = format_readable_date(datetime.now(self.tz))

        response = f"Today is {date}"

        return response

    def time(self, context: typing.Dict):
        time = format_readable_time(datetime.now(self.tz), self.hour_format)

        response = f"It is {time}"

        return response

    def day_of_week(self, context: typing.Dict):
        dow = datetime.now(self.tz).strftime('%A')

        response = f"It is {dow}"

        return response

    def set_timer(self, context: typing.Dict):
        entities = context['pos_info']['ENTITIES']

        node_id = context["node_id"]
        resp = self.ova.node_manager.call_node_api("GET", node_id, "/timer_remaining_time")
        remaining = resp.json()['time_remaining']

        response = ""

        if remaining == 0:
            if 'TIME' in entities:
                t = entities['TIME']
                #print(t)
                t_split = t.split()
                durration = 0
                for inc, m in {'second': 1, 'minute': 60, 'hour': 3600}.items():
                    for inc_idx, sec in enumerate(t_split):
                        if inc in sec:
                            d = t_split[inc_idx - 1]
                            durration += int(d) * m
                if durration > 0:
                    self.ova.node_manager.call_node_api("POST", node_id, "/set_timer", data={"durration": durration})
                    response = f"Setting a timer for {t}"
                else:
                    context['hub_callback'] = "default.set_timer"
                    return "How long should I set a timer for?"
            else:
                context['hub_callback'] = "default.set_timer"
                return "How long should I set a timer for?"
        else:
            return "There is already a timer running"

        return response  

    def time_remaining(self, context: typing.Dict):
        node_id = context["node_id"]
        resp = self.ova.node_manager.call_node_api("GET", node_id, "/timer_remaining_time")
        remaining = resp.json()['time_remaining']
        if remaining > 0:
            hours = 0
            minutes = 0
            seconds = 0
            if remaining == 0:
                return "The timer is up"
            if remaining % 3600 > 0:
                hours = remaining // 3600
                remaining = remaining % 3600
            if remaining % 60 > 0:
                minutes = remaining // 60
                seconds = remaining % 60
        
            pieces = []
            if hours > 0:
                pieces.append(f"{hours} hours")
            if minutes > 0:
                pieces.append(f"{minutes} minutes")
            if seconds > 0:
                pieces.append(f"{seconds} seconds")

            response = "There are "
            if len(pieces) > 1:
                response += ", ".join(pieces[:2])
                if len(pieces) > 2:
                    response += f" and {pieces[-1]}"
            else:
                response += f" {pieces[0]}"
            response += " remaining"
            return response
        else:
            return "There is no timer currently running"
    
    def stop_timer(self, context: typing.Dict):
        node_id = context["node_id"]
        resp = self.ova.node_manager.call_node_api("GET", node_id, "/stop_timer")
        return "Stopping the timer"

def build_skill(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    return Default(skill_config, ova)

def default_config():
    return {
        "name": "Default",
        "required_integrations": [],
        "timezone": "US/Eastern",
        "24_hour_format": False
    }