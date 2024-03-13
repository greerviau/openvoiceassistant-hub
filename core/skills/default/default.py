import typing
import logging
logger = logging.getLogger("skill.default")

from datetime import datetime

from core.utils.nlp.preprocessing import extract_numbers
from core.utils.nlp.formatting import format_readable_date, format_readable_time, format_seconds

class Default:

    def __init__(self, skill_config: typing.Dict, ova: "OpenVoiceAssistant"):
        self.ova = ova

        self.hour_format = "%H" if skill_config["24_hour_format"] else "%I"

    def introduction(self, context: typing.Dict):
        context["response"] = "Hello. My name is ova. I am an opensource and locally controlled voice assistant. I am designed to be an offline alternative to popular voice assistants like Alexa and Google home."

    def volume(self, context: typing.Dict):
        node_id = context["node_id"]
        command = context["cleaned_command"]

        numbers = extract_numbers(command)
        try:
            value = int(numbers[0])
        except:
            context["response"] = "No volume percentage specified"
            return

        if "percent" in command or value > 10:
            response = f"Setting the volume to {value} percent"
            volume_percent = value
        else:
            response = f"Setting the volume to {value}"
            volume_percent = value * 10

        node_config = self.ova.node_manager.get_node_config(node_id)
        node_config["volume"] = volume_percent
        self.ova.node_manager.update_node_config(node_id, node_config)

        resp = self.ova.node_manager.call_node_api("PUT", node_id, "/volume/set", json={"volume_percent": volume_percent})
        try:
            resp.raise_for_status()
        except:
            response = "Failed to set timer"

        context["response"] = response
    
    def date(self, context: typing.Dict):
        date = datetime.now().strftime("%B %d, %Y")
        readable_date = format_readable_date(datetime.now())
        
        context["synth_response"] = f"Today is {readable_date}"
        context["response"] = f"Today is {date}"

    def time(self, context: typing.Dict):
        time = datetime.now().strftime(f"{self.hour_format}:%M").lstrip("0")
        readable_time = format_readable_time(datetime.now(), self.hour_format)

        context["synth_response"] = f"It is {readable_time}"
        context["response"] = f"It is {time}"

    def day_of_week(self, context: typing.Dict):
        dow = datetime.now().strftime("%A")

        response = f"It is {dow}"
        context["response"] = response

    def set_timer(self, context: typing.Dict):
        entities = context["sent_info"]["ENTITIES"]

        try:
            node_id = context["node_id"]
            resp = self.ova.node_manager.call_node_api("GET", node_id, "/timer/remaining")
            remaining = resp.json()["time_remaining"]
        except:
            context["response"] = "Failed to start the timer."
            return

        if remaining == 0:
            try:
                if "TIME" in entities:
                    t = entities["TIME"]
                    t_split = t.split()
                    if t_split[0] in ["a", "an"]:
                        t_split[0] = 1
                    durration = 0
                    for inc, m in {"second": 1, "minute": 60, "hour": 3600}.items():
                        for inc_idx, sec in enumerate(t_split):
                            if inc in sec:
                                d = t_split[inc_idx - 1]
                                durration += int(d) * m
                    if durration > 0:
                        self.ova.node_manager.call_node_api("POST", node_id, "/timer/set", json={"durration": durration})
                        response = f"Setting a timer for {format_seconds(durration)}"
                    else:
                        raise RuntimeError("No time durration specified")
                else:
                    raise RuntimeError("No time durration specified")
            except RuntimeError:
                context["hub_callback"] = "default.set_timer"
                response = "How long should I set a timer for?"
        else:
            response = "There is already a timer running"

        context["response"] = response 

    def time_remaining(self, context: typing.Dict):
        try:
            node_id = context["node_id"]
            resp = self.ova.node_manager.call_node_api("GET", node_id, "/timer/remaining")
            remaining = resp.json()["time_remaining"]
        except:
            context["response"] = "I was unable to get the remaining time."
            return

        if remaining > 0:
            if remaining == 0:
                context["response"] = "The timer is up"
                return
            
            response = f"There are {format_seconds(remaining)}"
        else:
            response = "There is no timer currently running"
        context["response"] = response
    
    def stop_timer(self, context: typing.Dict):
        try:
            node_id = context["node_id"]
            resp = self.ova.node_manager.call_node_api("GET", node_id, "/timer/remaining")
            remaining = resp.json()["time_remaining"]
        except:
            context["response"] = "I was unable to get the remaining time."
            return

        if remaining == 0:
            context["response"] = "There is no timer currently running"
            return

        node_id = context["node_id"]
        resp = self.ova.node_manager.call_node_api("POST", node_id, "/timer/stop")
        context["response"] =  "Stopping the timer"