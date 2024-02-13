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
            context['response'] = ''
        else:
            if self.ova.skill_manager.skill_imported(skill):
                try:
                    getattr(self.ova.skill_manager.get_skill_module(skill), action)(context)
                except Exception as e:
                    context['response'] = f"Sorry. While executing that action, I encountered the following problem. {str(e)}"
            else:
                context['response'] = 'Skill is not imported.'
        if 'response' not in context:
            context['response'] = ""
        if 'synth_response' not in context:
            context['synth_response'] = context['response']

        dt = time.time() - start
        print("Time to run action: ", dt)
        context['time_to_action'] = dt