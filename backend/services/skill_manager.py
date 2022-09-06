import importlib

class SkillManager:
    def __init__(self, config: dict):
        self.imported_skills = config['imported_skills']
        self.skill_imports = {}
        for skill, config in self.imported_skills.items():
            print('Importing ', skill)
            self.import_skill(skill, config)

    def add_skill(self, skill, config):
        if skill not in self.imported_skills:
            self.imported_skills[skill] = config

    def update_skill(self, skill, config):
        if skill in self.imported_skills:
            self.imported_skills[skill] = config   

    def get_skill_config(self, skill):
        return self.imported_skills[skill]

    def is_skill_imported(self, skill):
        return skill in self.imported_skills

    def list_imported_skills(self):
        return list(self.imported_skills.keys())

    def import_skill(self, skill, config):
        module = importlib.import_module(f'skills.{skill}')
        self.skill_imports[skill] = module.build_skill(config)

    def skill_action(self, context):
        skill = context['skill']
        action = context['action']
        method = getattr(self.skill_imports[skill], action)
        method(context)