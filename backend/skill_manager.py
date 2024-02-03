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

    def add_skill(self, skill_id: str):
        if not self.skill_imported(skill_id):
            self.__import_skill(skill_id, None)
        else:
            raise RuntimeError('Skill is already imported')

    def remove_skill(self, skill_id: str):
        if self.skill_imported(skill_id):
            skill_config = self.skills.pop(skill_id)
            self.not_imported.append(skill_id)
            config.set("skills", self.skills)
            return skill_config
        raise RuntimeError("Skill not imported")

    def update_skill_config(self, skill_id: str, skill_config: typing.Dict):
        imported = self.skill_imported(skill_id)
        self.__import_skill(skill_id, skill_config)
        if not imported: self.not_imported.remove(skill_id)

    def get_skill_config(self, skill_id: str) -> typing.Dict:
        if self.skill_imported(skill_id):
            return self.skills[skill_id]
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
    
    def get_skill_module(self, skill_id: str):
        if self.skill_imported(skill_id):
            return self.imported_skill_modules[skill_id]
        
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
                self.__save_config(skill_id, skill_config)
            try:
                module = importlib.import_module(f'backend.skills.{skill_id}')
                self.imported_skill_modules[skill_id] = module.build_skill(skill_config, self.ova)
                self.__save_config(skill_id, skill_config)
            except Exception as e:
                raise RuntimeError(f'Failed to load {skill_id} | Exception {repr(e)}')
        else:
            raise RuntimeError('Skill does not exist')
        
    def __save_config(self, skill_id: str, skill_config: typing.Dict):
        config.set('skills', skill_id, skill_config)