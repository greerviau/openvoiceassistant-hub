import importlib
import typing
from pkgutil import iter_modules

from backend import config
from backend import integrations

class IntegrationManager:
    def __init__(self, ova):
        self.ova = ova

        self.imported_integration_modules = {}

        self.available_integrations = [submodule.name for submodule in iter_modules(integrations.__path__)]

        self.integrations = config.get('integrations')
        self.not_imported = [integration for integration in self.available_integrations if integration not in self.integrations]

        print('Importing integrations...')
        for integration_id in self.integrations:
            integration_config = config.get('integrations', integration_id)
            if not integration_config:
                integration_config = self.get_default_integration_config(integration_id)
            self.__import_integration(integration_id, integration_config)

    @property
    def imported_integrations(self):
        return list(self.integrations.keys())
    
    def integration_imported(self, integration_id: str):
        return integration_id in self.imported_integration_modules

    def integration_exists(self, integration_id: str):
        return integration_id in self.available_integrations

    def remove_integration(self, integration_id: str):
        if self.integration_imported(integration_id):
            integration_config = self.integrations.pop(integration_id)
            self.imported_integration_modules.pop(skill_id)
            self.imported_integrations.remove(integration_id)
            self.not_imported.append(integration_id)
            config.set("integrations", self.integrations)
            return integration_config
        raise RuntimeError("Integration not imported")

    def update_integration_config(self, integration_id: str, integration_config: typing.Dict):
        if self.integration_exists(integration_id):
            imported = self.integration_imported(integration_id)
            self.__import_integration(integration_id, integration_config)
            if not imported: self.not_imported.remove(integration_id)
        else:
            raise RuntimeError("Integration does not exist")

    def get_integration_config(self, integration_id: str) -> typing.Dict:
        if self.integration_exists(integration_id):
            if self.integration_imported(integration_id):
                return self.integrations[integration_id]
            else:
                return self.get_default_integration_config(integration_id)
        else:
            raise RuntimeError('Integration does not exist')

    def get_default_integration_config(self, integration_id: str) -> typing.Dict:
        if self.integration_exists(integration_id):
            module = importlib.import_module(f'backend.integrations.{integration_id}')
            return module.default_config()
        else:
            raise RuntimeError('Integration does not exist')
    
    def get_integration_module(self, integration_id: str):
        if self.integration_imported(integration_id):
            return self.imported_integration_modules[integration_id]

    def __import_integration(self, integration_id: str, integration_config: typing.Dict):
        if self.integration_exists(integration_id):
            print('Importing ', integration_id)
            if not integration_config:
                integration_config = self.get_default_integration_config(integration_id)
                self.__save_config(integration_id, integration_config)
            try:
                module = importlib.import_module(f'backend.integrations.{integration_id}')
                self.imported_integration_modules[integration_id] = module.build_integration(integration_config, self.ova)
                self.__save_config(integration_id, integration_config)
            except Exception as e:
                raise RuntimeError(f'Failed to load {integration_id} | Exception {repr(e)}')
        else:
            raise RuntimeError('integration does not exist')
        
    def __save_config(self, integration_id: str, integration_config: typing.Dict):
        config.set('integrations', integration_id, integration_config)