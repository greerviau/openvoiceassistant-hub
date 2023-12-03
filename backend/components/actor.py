import time

from backend.schemas import Context

class Actor:
    def __init__(self, ova: 'OpenVoiceAssistant'):
        self.ova = ova

    def run_stage(self, context: Context):
        print('Skill Stage')
        skill = context['skill']
        action = context['action']

        start = time.time()

        if skill == 'DID_NOT_UNDERSTAND':
            context['response'] = 'Sorry, I did not understand'
        else:
            if self.ova.skill_manager.skill_imported(skill):
                method = getattr(self.ova.skill_manager.get_skill_module(skill), action)
                context['response'] = method(context)
            else:
                context['response'] = 'Skill is not imported'

        context['time_to_action'] = time.time() - start