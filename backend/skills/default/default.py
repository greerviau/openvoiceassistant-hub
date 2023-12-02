from typing import Dict
from datetime import datetime
import pytz
import threading
import time

from backend import config
from backend.utils.nlp import try_parse_word_number, extract_numbers

class ThreadTimer(threading.Timer):
    started_at = None
    def start(self):
        self.started_at = time.time()
        threading.Timer.start(self)
    def elapsed(self):
        return time.time() - self.started_at
    def remaining(self):
        rem = self.interval - self.elapsed()
        if rem > 0:
            return rem
        return 0

class Default:

    def __init__(self, config: Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova
        self.config = config

        self.tz = pytz.timezone(config["timezone"])
        self.format = "%H" if config["24_hour_format"] else "%I"

        self.timer = None
        self.timer_node_id = None

    def volume(self, context: Dict):
        node_id = context["node_id"]
        command = context['cleaned_command']

        numbers = extract_numbers(command)
        numbers.extend([try_parse_word_number(word) for word in command.split() if word])

        value = numbers[0]

        if 'percent' in command or value > 10:
            response = f"Setting the volume to {value} percent"
            volume_percent = value
        else:
            response = f"Setting the volume to {value}"
            volume_percent = value * 10


        self.ova.node_manager.call_node_api("PUT", node_id, "/set_volume", data={"volume": volume_percent})
        return response

    def hello(self, context: Dict):
        command = context['cleaned_command']
        addr = context['addr'] if 'addr' in context else ''

        response = ''
        if 'morning' in command:
            response = f'Good morning {addr}'
        elif 'afternoon' in command:
            response = f'Good afternoon {addr}'
        elif 'evening' in command:
            response = f'Good evening {addr}'
        elif 'night' in command:
            response = f'Good night {addr}'
        else:
            response = f'Hello {addr}'

        return response

    def how_are_you(self, context: Dict):
        command = context['cleaned_command']
        addr = context['addr'] if 'addr' in context else ''

        response = f'Doing well {addr}'

        return response

    def whats_up(self, context: Dict):
        command = context['cleaned_command']
        addr = context['addr'] if 'addr' in context else ''

        response = f'Not much {addr}'
        
        return response

    def goodbye(self, context: Dict):
        command = context['cleaned_command']
        addr = context['addr'] if 'addr' in context else ''

        response = f'Goodbye {addr}'

        return response

    def thank_you(self, context: Dict):
        command = context['cleaned_command']
        addr = context['addr'] if 'addr' in context else ''

        response = f'Youre Welcome {addr}'

        return response
    
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

    def set_timer(self, context: Dict):
        
        def alert_timer_finished(self):
            print('Timer finished')
            self.ova.node_manager.call_node_api("POST", self.timer_node_id, "/play_alarm")

        command = context['cleaned_command']

        entities = context['pos_info']['ENTITIES']

        response = ""

        if not self.timer:
            if 'TIME' in entities:
                t = entities['TIME']
                for inc, m in {'second': 1, 'minute': 60, 'hour': 3600}.items():
                    if inc in t:
                        d = t.replace(inc, '').strip().split()[0]
                        response = f"Setting a timer for {t}"
                        d = try_parse_word_number(d)
                        d = d * m
                        self.timer = ThreadTimer(d, alert_timer_finished)
                        self.timer_node_id = context["node_id"]
                        self.timer.start()
                        break
                if not response:
                    context['hub_callback'] = "timer.set_timer"
                    return "How long should I set a timer for?"
            else:
                context['hub_callback'] = "timer.set_timer"
                return "How long should I set a timer for?"
        else:
            return "There is already a timer running"

        return response  

    def time_remaining(self, context: Dict):
        command = context['cleaned_command']

        if self.timer:
            hours = 0
            minutes = 0
            seconds = 0
            remaining = int(self.timer.remaining())
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
    
    def stop_timer(self, context: Dict):
        if self.timer:
            self.timer.cancel()
            self.ova.node_manager.call_node_api("POST", self.timer_node_id, "/stop_alarm")
            self.timer = None
            self.timer_node_id = None

            return "Stopping the timer"
        else:
            return "There is no timer currently running"

def build_skill(config: Dict, ova: 'OpenVoiceAssistant'):
    return Default(config, ova)

def default_config():
    return {
        "timezone": "US/Eastern",
        "24_hour_format": False
    }