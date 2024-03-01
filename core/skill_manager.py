import importlib
import typing
import subprocess
from pkgutil import iter_modules

from core import config
from core import skills

class SkillManager:
    def __init__(self, ova):
        self.ova = ova

        self.imported_skill_modules = {}

        self.available_skills = [submodule.name for submodule in iter_modules(skills.__path__)]
        self.available_skills = {skill: self.get_skill_manifest(skill) for skill in self.available_skills}

        self.skills = config.get('skills')

        print('Importing Skills...')
        for skill_id, manifest in self.skills.items():
            if self.skill_exists(skill_id):
                self.__import_skill(skill_id, manifest)
            else:
                self.skills.pop(skill_id)
                config.set('skills', self.skills)
                print(f"Removing {skill_id}")

    @property
    def imported_skills(self):
        return [manifest for manifest in self.skills.values()]

    @property
    def not_imported_skills(self):
        return [manifest for _id, manifest in self.available_skills.items() if _id not in self.skills]

    def skill_imported(self, skill_id: str):
        return skill_id in self.imported_skill_modules

    def skill_exists(self, skill_id: str):
        return skill_id in self.available_skills

    def remove_skill(self, skill_id: str):
        if self.skill_imported(skill_id):
            manifest = self.skills.pop(skill_id)
            self.imported_skill_modules.pop(skill_id)
            config.set("skills", self.skills)
            return manifest
        raise RuntimeError("Skill not imported")

    def update_skill(self, skill_id: str, skill_config: typing.Dict):
        if self.skill_exists(skill_id):
            if not self.skill_imported(skill_id):
                manifest = self.get_skill_manifest(skill_id)
                if skill_config:
                    manifest["config"] = skill_config
            else:
                manifest = self.skills[skill_id]
                if skill_config:
                    manifest["config"] = skill_config
            self.__import_skill(skill_id, manifest)
        else:
            raise RuntimeError("Skill does not exist")

    def check_for_discrepancy(self, new: typing.Dict, default: typing.Dict):
        if list(default.keys()) == list(new.keys()):
            return new
        new_clone = new.copy()
        for key, value in default.items():
            if key not in new_clone:
                new_clone[key] = value
        for key, value in new.items():
            if key not in default:
                new_clone.pop(key)
        return new_clone
        
    def get_skill_config(self, skill_id: str) -> typing.Dict:
        if self.skill_exists(skill_id):
            if self.skill_imported(skill_id) and "config" in self.skills[skill_id]:
                return self.skills[skill_id]["config"]
            else:
                return self.get_default_skill_config(skill_id)
        else:
            raise RuntimeError('Skill does not exist')

    def get_default_skill_config(self, skill_id: str) -> typing.Dict:
        if self.skill_exists(skill_id):
            manifest = self.get_skill_manifest(skill_id)
            if "config" in manifest:
                return manifest["config"]
            return {}
        else:
            raise RuntimeError('Skill does not exist')
        
    def get_skill_manifest(self, skill_id: str) -> typing.Dict:
        if self.skill_exists(skill_id):
            if self.skill_imported(skill_id):
                return self.skills[skill_id]
            else:
                return self.get_default_skill_manifest(skill_id)
        else:
            raise RuntimeError('Skill does not exist')

    def get_default_skill_manifest(self, skill_id: str) -> typing.Dict:
        if self.skill_exists(skill_id):
            module = importlib.import_module(f'core.skills.{skill_id}')
            return module.manifest()
        else:
            raise RuntimeError('Skill does not exist')
    
    def get_skill_module(self, skill_id: str):
        if self.skill_imported(skill_id):
            return self.imported_skill_modules[skill_id]
        else:
            raise RuntimeError("Skill is not imported")
        
    def get_skill_intents(self, skill_id: str):
        if self.skill_exists(skill_id):
            module = importlib.import_module(f'core.skills.{skill_id}')
            return module.INTENTIONS
        else:
            raise RuntimeError('Skill does not exist')

    def __import_skill(self, skill_id: str, manifest: typing.Dict):
        if self.skill_exists(skill_id):
            print('Importing ', skill_id)
            default_manifest = self.get_default_skill_manifest(skill_id)
            manifest = self.check_for_discrepancy(manifest, default_manifest)
            if "requirements" in manifest:
                requirements = manifest["requirements"]
                command = ["pip", "install"] + requirements
                try:
                    subprocess.check_output(command)
                except Exception as e:
                    raise RuntimeError(f"Failed to install skill requirements | {repr(e)}")
            if "config" in manifest:
                skill_config = manifest["config"]
                default_config = self.get_default_skill_config(skill_id)
                if not skill_config:
                    skill_config = default_config
                else:
                    skill_config = self.check_for_discrepancy(skill_config, default_config)
                manifest["config"] = skill_config
            else:
                skill_config = {}
            self.skills[skill_id] = manifest
            config.set('skills', self.skills)
            try:
                module = importlib.import_module(f'core.skills.{skill_id}')
                self.imported_skill_modules[skill_id] = module.build_skill(skill_config, self.ova)
            except Exception as e:
                print(f'Failed to load {skill_id} | Exception {repr(e)}')
                # TODO
                # custom exception for this
                # in the future use it to extablish that skill is crashed
                # update flag in config and display on FE
                # can do same thing for integrations and even components
        else:
            raise RuntimeError('Skill does not exist')