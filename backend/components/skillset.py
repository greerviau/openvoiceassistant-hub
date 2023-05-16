import importlib
import os
import typing
import time
from pkgutil import iter_modules

from backend.enums import Components
from backend import config
from backend import skills
from backend.schemas import Context

class Skillset:
    def __init__(self, ova: 'OpenVoiceAssistant'):
        self.ova = ova
        self.available_skills = []
        for submodule in iter_modules(skills.__path__):
            sm = submodule.name
            nested_modules = [module for module in iter_modules(importlib.import_module(f'backend.skills.{sm}').__path__) if module.ispkg]
            print(nested_modules)
            if not any(nested_modules): 
                self.available_skills.append(sm)
            else:
                self.available_skills.extend([f'{sm}.{m.name}' for m in nested_modules])
        print(self.available_skills)
        
        self.imported_skills = config.get(Components.Skillset.value, 'imported_skills')
        self.not_imported = list(set(self.available_skills + self.imported_skills))

        self.imported_skill_modules = {}

        for skill_id in self.imported_skills:
            print('Importing ', skill_id)
            skill_config = config.get(Components.Skillset.value, 'skill_configs', *skill_id.split('.'))
            if not skill_config: 
                skill_config = self.get_default_skill_config(skill_id)
            self.__import_skill(skill_id, skill_config)

    def add_skill(self, skill_id: str):
        if not self.skill_imported(skill_id):
            self.__import_skill(skill_id, None)
        else:
            raise RuntimeError('Skill is already imported')

    def add_skill_config(self, skill_id: str, skill_config: typing.Dict):
        if not self.skill_imported(skill_id):
            self.__import_skill(skill_id, skill_config)
        else:
            raise RuntimeError('Skill is already imported')

    def update_skill_config(self, skill_id: str, skill_config: typing.Dict):
        if self.skill_imported(skill_id):
            self.__import_skill(skill_id, skill_config)
        else:
            raise RuntimeError('Skill is not imported')

    def get_skill_config(self, skill_id: str) -> typing.Dict:
        if self.skill_imported(skill_id):
            return config.get(Components.Skillset.value, 'skill_configs', *skill_id.split('.'))
        else:
            return self.get_default_skill_config(skill_id)

    def get_default_skill_config(self, skill_id: str) -> typing.Dict:
        if self.skill_exists(skill_id):
            module = importlib.import_module(f'backend.skills.{skill_id}')
            return module.default_config()
        else:
            raise RuntimeError('Skill does not exist')

    def skill_imported(self, skill_id: str):
        return skill_id in self.imported_skill_modules

    def skill_exists(self, skill_id: str):
        return skill_id in self.available_skills

    def run_stage(self, context: Context):
        print('Skill Stage')
        skill = context['skill']
        action = context['action']

        start = time.time()

        if skill == 'DID_NOT_UNDERSTAND':
            context['response'] = 'Sorry, I did not understand'
        else:
            if self.skill_imported(skill):
                method = getattr(self.imported_skill_modules[skill], action)
                context['response'] = method(context)
            else:
                context['response'] = 'Skill is not imported'

        context['time_to_action'] = time.time() - start

    def __import_skill(self, skill_id: str, skill_config: typing.Dict):
        if self.skill_exists(skill_id):
            if skill_id not in self.imported_skills:
                self.imported_skills.append(skill_id)
                config.set(Components.Skillset.value, 'imported_skills', self.imported_skills)

            module = importlib.import_module(f'backend.skills.{skill_id}')
            if skill_config is None:
                skill_config = module.default_config()
                self.__save_config(skill_id, skill_config)
            try:
                self.imported_skill_modules[skill_id] = module.build_skill(skill_config, self.ova)
            except Exception as e:
                raise RuntimeError(f'Failed to load {skill_id} | Exception {repr(e)}')
        else:
            raise RuntimeError('Skill does not exist')
        
    def __save_config(self, skill_id: str, skill_config: typing.Dict):
        config.set(Components.Skillset.value, 'skill_configs', *skill_id.split('.'), skill_config)