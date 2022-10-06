import importlib
import os
import typing

from backend.config import Configuration
import backend.skills as skills
from pkgutil import iter_modules

class Skillset:
    def __init__(self, config: Configuration):
        self.config = config
        
        self.available_skills = [submodule.name for submodule in iter_modules(skills.__path__)]
        self.imported_skills = self.config.get('components', 'skillset', 'imported_skills')
        print('Imported_skills:')
        for skill in self.imported_skills:
            print(skill)
        self.not_imported = list(set(self.available_skills + list(self.imported_skills.keys())))

        self.skill_imports = {}
        for skill, config in self.imported_skills.items():
            print('Importing ', skill)
            self.__import_skill(skill, config)

    def add_skill(self, skill: str):
        if not self.skill_imported(skill):
            self.__import_skill(skill, None)
        else:
            raise RuntimeError('Skill is already imported')

    def add_skill_config(self, skill: str, config: typing.Dict): # TODO use TypedDict
        if not self.skill_imported(skill):
            self.__import_skill(skill, config)
        else:
            raise RuntimeError('Skill is already imported')

    def update_skill_config(self, skill: str, config):
        if self.skill_imported(skill):
            self.__import_skill(skill, config)
        else:
            raise RuntimeError('Skill is not imported')

    def get_skill_config(self, skill: str) -> typing.Dict: # TODO use TypedDict
        if self.skill_imported(skill):
            return self.imported_skills[skill]
        raise RuntimeError('Skill is not imported')

    def skill_imported(self, skill: str):
        return skill in self.imported_skills

    def skill_exists(self, skill: str):
        return skill in self.available_skills

    def run_stage(self, context: typing.Dict):  # TODO use TypedDict
        print('Skill Stage')
        skill = context['skill']
        action = context['action']
        if self.skill_imported(skill):
            method = getattr(self.skill_imports[skill], action)
            method(context)

    def __import_skill(self, skill: str, config: typing.Dict):  # TODO use TypedDict
        if self.skill_exists(skill):
            module = importlib.import_module(f'backend.skills.{skill}')
            if config is None:
                config = module.default_config()
                self.imported_skills[skill] = config
                self.config.setkey('components', 'skillset', 'imported_skills', skill, value=config)
            self.skill_imports[skill] = module.build_skill(config)
        else:
            raise RuntimeError('Skill does not exist')