import typing
import time

from backend.config import Configuration
from backend.components.understander.classifier import Classifier
from backend.utils.nlp import clean_text

class Understander:
    def __init__(self, config: Configuration):
        self.config = config

        self.classifier = Classifier(self.config)
        self.wake_word = self.config.get('wake_word')
        self.engage_delay = self.config.get('engage_delay')

        self.conf_thresh = self.config.get('components', 'understander', 'conf_thresh')

    def understand(self, command: str) -> typing.Tuple[str, str, float]:
        skill, action, conf = self.classifier.predict_intent(command)
        
        print(f'Skill: {skill}')
        print(f'Action: {action}')
        print(f'Conf: {conf}')
    
        return skill, action, conf
    
    def run_stage(self, context: typing.Dict):
        print('Understanding Stage')
        command = context['command']

        engage = context['engage']
        cleaned_command = clean_text(command)
        context['cleaned_command'] = cleaned_command

        time_sent = context['time_sent']
        last_time_engaged = context['last_time_engaged']

        delta_time = time_sent - last_time_engaged

        start = time.time()

        if engage or self.wake_word in cleaned_command or delta_time < self.engage_delay:
            skill, action, conf = self.understand(cleaned_command)
            context['time_to_understand'] = time.time() - start
            context['skill'] = skill
            context['action'] = action
            context['conf'] = conf
            
            if conf < self.conf_thresh:
                raise RuntimeError('Not confident in skill')
        else:
            raise RuntimeError('Command does not engage')

