import importlib
import typing
from pkgutil import iter_modules

from backend import config
from backend import integrations

class IntegrationManager:
    def __init__(self, ova):
        self.ova = ova

        self.available_integrations = []
        for submodule in iter_modules(integrations.__path__):
            sm = submodule.name
            self.available_integrations.append(sm)

        self.integrations = config.get('integrations')
        self.imported_integrations = list(self.integrations.keys())
        self.not_imported = [integration for integration in self.available_integrations if integration not in self.imported_integrations]

        self.imported_integration_modules = {}

        print('Importing Integrations...')
        for integration_id in self.imported_integrations:
            integration_config = config.get('integrations', integration_id)
            if not integration_config:
                integration_config = self.get_default_integration_config(integration_id)
            self.__import_integration(integration_id, integration_config)

    def add_integration(self, integration_id: str):
        if not self.integration_imported(integration_id):
            self.__import_integration(integration_id, None)
        else:
            raise RuntimeError('Integration is already imported')

    def remove_integration(self, integration_id: str):
        if self.integration_imported(integration_id):
            integration_config = self.integrations.pop(integration_id)
            self.imported_integrations.remove(integration_id)
            self.not_imported.append(integration_id)
            config.set("integrations", self.integrations)
            return integration_config
        raise RuntimeError("Integration not imported")

    def update_integration_config(self, integration_id: str, integration_config: typing.Dict):
        self.__import_integration(integration_id, integration_config)

    def get_integration_config(self, integration_id: str) -> typing.Dict:
        if self.integration_imported(integration_id):
            return config.get('integrations', *integration_id.split('.'))
        else:
            return self.get_default_integration_config(integration_id)

    def get_default_integration_config(self, integration_id: str) -> typing.Dict:
        if self.integration_exists(integration_id):
            module = importlib.import_module(f'backend.integrations.{integration_id}')
            return module.default_config()
        else:
            raise RuntimeError('Integration does not exist')

    def integration_imported(self, integration_id: str):
        return integration_id in self.imported_integration_modules

    def integration_exists(self, integration_id: str):
        return integration_id in self.available_integrations
    
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
            except Exception as e:
                raise RuntimeError(f'Failed to load {integration_id} | Exception {repr(e)}')
        else:
            raise RuntimeError('Integration does not exist')
        
    def __save_config(self, integration_id: str, integration_config: typing.Dict):
        config.set('integrations', integration_id, integration_config)