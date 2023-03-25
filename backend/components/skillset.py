import importlib
import os
import typing
import time
from pkgutil import iter_modules

from backend import config
from backend import skills
from backend.schemas import Context

class Skillset:
    def __init__(self):
        self.available_skills = [submodule.name for submodule in iter_modules(skills.__path__)]
        imported_skill_configs = config.get('components', 'skillset', 'imported_skills')
        print('Imported Skills')
        for skill in imported_skill_configs:
            print(skill)
        self.not_imported = list(set(self.available_skills + list(imported_skill_configs.keys())))

        self.imported_skills = {}
        for skill_id, skill_config in imported_skill_configs.items():
            print('Importing ', skill_id)
            self.__import_skill(skill_id, skill_config)

    def add_skill(self, skill: str):
        if not self.skill_imported(skill):
            self.__import_skill(skill, None)
        else:
            raise RuntimeError('Skill is already imported')

    def add_skill_config(self, skill: str, skill_config: typing.Dict):
        if not self.skill_imported(skill):
            self.__import_skill(skill, skill_config)
        else:
            raise RuntimeError('Skill is already imported')

    def update_skill_config(self, skill: str, skill_config: typing.Dict):
        if self.skill_imported(skill):
            self.__import_skill(skill, skill_config)
        else:
            raise RuntimeError('Skill is not imported')

    def get_skill_config(self, skill_id: str) -> typing.Dict:
        if self.skill_imported(skill_id):
            return self.imported_skills[skill_id].config
        else:
            return self.get_default_skill_config(skill_id)

    def get_default_skill_config(self, skill_id: str) -> typing.Dict:
        if self.skill_exists(skill_id):
            module = importlib.import_module(f'backend.skills.{skill_id}')
            return module.default_config()
        else:
            raise RuntimeError('Skill does not exist')

    def skill_imported(self, skill: str):
        return skill in self.imported_skills

    def skill_exists(self, skill: str):
        return skill in self.available_skills

    def run_stage(self, context: Context):
        print('Skill Stage')
        skill = context['skill']
        action = context['action']

        start = time.time()

        if self.skill_imported(skill):
            method = getattr(self.imported_skills[skill], action)
            context['response'] = method(context)
            context['time_to_action'] = time.time() - start

    def __import_skill(self, skill: str, skill_config: typing.Dict):
        if self.skill_exists(skill):
            module = importlib.import_module(f'backend.skills.{skill}')
            if skill_config is None:
                skill_config = module.default_config()
            config.set('components', 'skillset', 'imported_skills', skill, value=skill_config)
            self.imported_skills[skill] = module.build_skill(skill_config)
        else:
            raise RuntimeError('Skill does not exist')