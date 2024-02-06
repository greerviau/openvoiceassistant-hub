import importlib
import typing
from pkgutil import iter_modules

from backend import config
from backend import skills

class SkillManager:
    def __init__(self, ova):
        self.ova = ova

        self.imported_skill_modules = {}

        self.available_skills = [submodule.name for submodule in iter_modules(skills.__path__)]

        self.skills = config.get('skills')
        self.not_imported = [skill for skill in self.available_skills if skill not in self.skills]

        print('Importing Skills...')
        for skill_id in self.skills:
            skill_config = config.get('skills', skill_id)
            if not skill_config:
                skill_config = self.get_default_skill_config(skill_id)
            self.__import_skill(skill_id, skill_config)

    @property
    def imported_skills(self):
        return list(self.skills.keys())

    def skill_imported(self, skill_id: str):
        return skill_id in self.imported_skill_modules

    def skill_exists(self, skill_id: str):
        return skill_id in self.available_skills

    def remove_skill(self, skill_id: str):
        if self.skill_imported(skill_id):
            skill_config = self.skills.pop(skill_id)
            self.imported_skill_modules.pop(skill_id)
            self.not_imported.append(skill_id)
            config.set("skills", self.skills)
            return skill_config
        raise RuntimeError("Skill not imported")

    def update_skill_config(self, skill_id: str, skill_config: typing.Dict):
        if self.skill_exists(skill_id):
            imported = self.skill_imported(skill_id)
            self.__import_skill(skill_id, skill_config)
            if not imported: self.not_imported.remove(skill_id)
        else:
            raise RuntimeError("Skill does not exist")

    def check_for_config_discrepancy(self, skill_id: str, skill_config: typing.Dict):
        default_skill_config = self.get_default_skill_config(skill_id)
        if list(default_skill_config.keys()) == list(skill_config.keys()):
            return skill_config
        skill_config_clone = skill_config.copy()
        for key, value in default_skill_config.items():
            if key not in skill_config:
                skill_config_clone[key] = value
                update_needed = True
        for key, value in skill_config.items():
            if key not in default_skill_config:
                skill_config_clone.pop(key)
        return skill_config_clone
        
    def get_skill_config(self, skill_id: str) -> typing.Dict:
        if self.skill_exists(skill_id):
            if self.skill_imported(skill_id):
                return self.skills[skill_id]
            else:
                return self.get_default_skill_config(skill_id)
        else:
            raise RuntimeError('Skill does not exist')

    def get_default_skill_config(self, skill_id: str) -> typing.Dict:
        if self.skill_exists(skill_id):
            module = importlib.import_module(f'backend.skills.{skill_id}')
            return module.default_config()
        else:
            raise RuntimeError('Skill does not exist')
    
    def get_skill_module(self, skill_id: str):
        if self.skill_imported(skill_id):
            return self.imported_skill_modules[skill_id]
        else:
            raise RuntimeError("Skill is not imported")
        
    def get_skill_intents(self, skill_id: str):
        if self.skill_exists(skill_id):
            module = importlib.import_module(f'backend.skills.{skill_id}')
            return module.INTENTIONS
        else:
            raise RuntimeError('Skill does not exist')

    def __import_skill(self, skill_id: str, skill_config: typing.Dict):
        if self.skill_exists(skill_id):
            print('Importing ', skill_id)
            if not skill_config:
                skill_config = self.get_default_skill_config(skill_id)
            else:
                skill_config = self.check_for_config_discrepancy(skill_id, skill_config)
            
            self.__save_config(skill_id, skill_config)
            try:
                module = importlib.import_module(f'backend.skills.{skill_id}')
                self.imported_skill_modules[skill_id] = module.build_skill(skill_config, self.ova)
            except Exception as e:
                raise RuntimeError(f'Failed to load {skill_id} | Exception {repr(e)}')
                # TODO
                # use this exception in the future to extablish that skill is crashed
                # update flag in config and display on FE
                # can do same thing for integrations and even components
        else:
            raise RuntimeError('Skill does not exist')
        
    def __save_config(self, skill_id: str, skill_config: typing.Dict):
        self.skills[skill_id] = skill_config
        config.set('skills', skill_id, skill_config)