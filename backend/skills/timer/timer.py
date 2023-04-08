from typing import Dict
import threading
import time

from backend import config
from backend.utils.nlp import ner, try_parse_word_number

class ThreadTimer(threading._Timer):
    started_at = None
    def start(self):
        self.started_at = time.time()
        threading._Timer.start(self)
    def elapsed(self):
        return time.time() - self.started_at
    def remaining(self):
        return self.interval - self.elapsed()

class Timer:

    def __init__(self, config: Dict):
        self.config = config

        self.timer = None

    def start_timer(self, context: Dict):
        command = context['command']

        ents = ner(command)

        response = ""

        if 'TIME' in ents:
            t = ents['TIME']
            for inc, m in {'second': 0, 'minute': 60, 'hour': 3600}.items():
                if inc in t:
                    d = t.replace(inc, '').strip()
                    response = f"Setting a timer for {t}"
                    d = try_parse_word_number(d)
                    d = d * m
                    print(d)
                    self.timer = ThreadTimer(d, self.alert_timer_finished)
                    self.timer.start()
            if not response:
                response = "How long should I set a timer for?"
                context['hub_callback'] = "timer.start_timer"
        else:
            response = "How long should I set a timer for?"
            context['hub_callback'] = "timer.start_timer"

        return response  

    def time_remaining(self, context: Dict):
        command = context['command']

        if self.timer:
            hours = 0
            minutes = 0
            seconds = 0
            remaining = int(self.timer.remaining())
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

            response = "There is"
            if len(pieces) > 1:
                response += ", ".join(pieces[:2])
                if len(pieces) > 2:
                    response += f" and {pieces[-1]}"
            else:
                response += f" {pieces[0]}"
            response += " remaining"
        else:
            response = "There is no timer currently running"

        return response

        return response

    def alert_timer_finished(self):
        print('Timer finished')


def build_skill(config: Dict):
    return Timer(config)

def default_config():
    return {}