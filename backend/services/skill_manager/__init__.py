import importlib

class SkillManager:
    def __init__(self, active_skills: dict):
        self.active_skills = active_skills
        self.skill_imports = {}
        for skill, config in active_skills.items():
            print('Importing ', skill)
            self.import_skill(skill, config)

    def set_skill_config(self, skill, config):
        self.active_skills[skill] = config

    def get_skill_config(self, skill):
        return self.active_skills[skill]

    def skill_is_active(self, skill):
        return skill in self.active_skills

    def list_active_skills(self):
        return list(self.active_skills.keys())

    def import_skill(self, skill, config):
        self.skill_imports[skill] = importlib.import_module(f'skills.{skill}')
        method = getattr(self.skill_imports[skill], 'init')
        method(config)

    def skill_response(self, context):
        skill = context['skill']
        action = context['action']
        method = getattr(self.skill_imports[skill], action)
        method(context)