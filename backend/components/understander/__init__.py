import typing

from backend.config import Configuration
from backend.components.understander.classifier import Classifier

class Understander:
    def __init__(self, config: Configuration):
        self.config = config

        self.classifier = Classifier(self.config)
        self.wake_word = self.config.get('wake_word')
        self.engage_delay = self.config.get('engage_delay')

    def understand(self, command: str):
        skill, action, conf = self.classifier.predict_intent(command)
        understanding = {}
        
        print(f'Skill: {skill}')
        print(f'Action: {action}')
        print(f'Conf: {conf}')
    
        return skill, action, conf
    
    def run_stage(self, context: typing.Dict):
        print('Understanding Stage')
        command = context['command']
        time_sent = context['time_sent']
        last_time_engaged = context['last_time_engaged']

        delta_time = time_sent - last_time_engaged

        if self.wake_word in command or delta_time < self.engage_delay:
            skill, action, conf = self.understand(command)
            context['skill'] = skill
            context['action'] = action
            context['conf'] = conf
        else:
            raise RuntimeError('Command does not engage')

