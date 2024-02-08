import time

from core.schemas import Context

class Actor:
    def __init__(self, ova: 'OpenVoiceAssistant'):
        self.ova = ova

    def run_stage(self, context: Context):
        print('Action Stage')
        start = time.time()

        skill = context['skill']
        action = context['action']
        pass_threshold = context['pass_threshold']

        if not pass_threshold:
            context['response'] = 'Sorry, I did not understand'
        elif skill in ["NO_COMMAND"]:
            context['response'] = ''
        else:
            if self.ova.skill_manager.skill_imported(skill):
                getattr(self.ova.skill_manager.get_skill_module(skill), action)(context)
                if 'synth_response' not in context:
                    context['synth_response'] = context['response']
            else:
                context['response'] = 'Skill is not imported'

        dt = time.time() - start
        print("Time to run action: ", dt)
        context['time_to_action'] = dt