from typing import Dict
import threading
import time

from backend import config
from backend.utils.nlp import named_entity_recognition, try_parse_word_number

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

class Timer:

    def __init__(self, config: Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova
        self.config = config

        self.timer = None
        self.node_id = None

    def set_timer(self, context: Dict):
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
                        self.timer = ThreadTimer(d, self.alert_timer_finished)
                        self.node_id = context["node_id"]
                        self.timer.start()
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

            response = "There is "
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
            self.ova.node_manager.call_node_api("POST", self.node_id, "/stop_alarm")
            self.timer = None
            self.node_id = None

            return "Stopping the timer"
        else:
            return "There is no timer currently running"

    def alert_timer_finished(self):
        print('Timer finished')
        self.ova.node_manager.call_node_api("POST", self.node_id, "/play_alarm")


def build_skill(config: Dict, ova: 'OpenVoiceAssistant'):
    return Timer(config, ova)

def default_config():
    return {}