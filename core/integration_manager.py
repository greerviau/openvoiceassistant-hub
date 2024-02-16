import importlib
import typing
from pkgutil import iter_modules

from core import config
from core import integrations

class IntegrationManager:
    def __init__(self, ova):
        self.ova = ova

        self.imported_integration_modules = {}

        self.available_integrations = [submodule.name for submodule in iter_modules(integrations.__path__)]

        self.integrations = config.get('integrations')
        self.not_imported = [integration for integration in self.available_integrations if integration not in self.integrations]

        print('Importing Integrations...')
        for integration_id in list(self.integrations.keys()):
            if self.integration_exists(integration_id):
                integration_config = config.get('integrations', integration_id)
                if not integration_config:
                    integration_config = self.get_default_integration_config(integration_id)
                self.__import_integration(integration_id, integration_config)
            else:
                self.integrations.pop(integration_id)
                config.set('integrations', self.integrations)
                print(f"Removing {integration_id}")

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
            self.imported_integration_modules.pop(integration_id)
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

    def check_for_config_discrepancy(self, integration_id: str, integration_config: typing.Dict):
        default_integration_config = self.get_default_integration_config(integration_id)
        if list(default_integration_config.keys()) == list(integration_config.keys()):
            return integration_config
        integration_config_clone = integration_config.copy()
        for key, value in default_integration_config.items():
            if key not in integration_config_clone:
                integration_config_clone[key] = value
        for key, value in integration_config_clone.items():
            if key not in default_integration_config:
                integration_config_clone.pop(key)
        return integration_config_clone
        
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
            module = importlib.import_module(f'core.integrations.{integration_id}')
            return module.default_config()
        else:
            raise RuntimeError('Integration does not exist')
    
    def get_integration_module(self, integration_id: str):
        if self.integration_imported(integration_id):
            return self.imported_integration_modules[integration_id]
        else:
            raise RuntimeError("Integration is not imported")
        
    def get_integration_intents(self, integration_id: str):
        if self.integration_exists(integration_id):
            module = importlib.import_module(f'core.integrations.{integration_id}')
            return module.INTENTIONS
        else:
            raise RuntimeError('Integration does not exist')

    def __import_integration(self, integration_id: str, integration_config: typing.Dict):
        if self.integration_exists(integration_id):
            print('Importing ', integration_id)
            if not integration_config:
                integration_config = self.get_default_integration_config(integration_id)
            else:
                integration_config = self.check_for_config_discrepancy(integration_id, integration_config)
            
            self.__save_config(integration_id, integration_config)
            try:
                module = importlib.import_module(f'core.integrations.{integration_id}')
                self.imported_integration_modules[integration_id] = module.build_integration(integration_config, self.ova)
            except Exception as e:
                print(f'Failed to load {integration_id} | Exception {repr(e)}')
                # TODO
                # custom exception for this
                # in the future use it to extablish that integration is crashed
                # update flag in config and display on FE
                # can do same thing for integrations and even components
        else:
            raise RuntimeError('Integration does not exist')
        
    def __save_config(self, integration_id: str, integration_config: typing.Dict):
        self.integrations[integration_id] = integration_config
        config.set('integrations', integration_id, integration_config)