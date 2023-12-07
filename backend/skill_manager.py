import importlib
import typing
from pkgutil import iter_modules

from backend import config
from backend import skills

class SkillManager:
    def __init__(self, ova):
        self.ova = ova

        self.available_skills = []
        for submodule in iter_modules(skills.__path__):
            sm = submodule.name
            self.available_skills.append(sm)

        self.skills = config.get('skills')
        self.imported_skills = list(self.skills.keys())
        self.not_imported = list(set(self.available_skills + self.imported_skills))

        self.imported_skill_modules = {}

        print('Importing Skills...')
        for skill_id in self.imported_skills:
            skill_config = config.get('skills', skill_id)
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
            return config.get('skills', *skill_id.split('.'))
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
        if self.skill_imported(skill_id):
            return self.imported_skill_modules[skill_id].INTENTIONS

    def __import_skill(self, skill_id: str, skill_config: typing.Dict):
        if self.skill_exists(skill_id):
            print('Importing ', skill_id)
            if not skill_config:
                skill_config = self.get_default_skill_config(skill_id)
                self.__save_config(skill_id, skill_config)
            try:
                module = importlib.import_module(f'backend.skills.{skill_id}')
                self.imported_skill_modules[skill_id] = module.build_skill(skill_config, self.ova)
            except Exception as e:
                raise RuntimeError(f'Failed to load {skill_id} | Exception {repr(e)}')
        else:
            raise RuntimeError('Skill does not exist')
        
    def __save_config(self, skill_id: str, skill_config: typing.Dict):
        config.set('skills', skill_id, skill_config)