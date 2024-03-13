import importlib
import typing
import subprocess
import logging
logger = logging.getLogger("integration_manager")

from pkgutil import iter_modules

from core import config
from core import integrations

class IntegrationManager:
    def __init__(self, ova):
        self.ova = ova

        self.imported_integration_modules = {}

        self.available_integrations = [submodule.name for submodule in iter_modules(integrations.__path__)]
        self.available_integrations = {integration: self.get_integration_manifest(integration) for integration in self.available_integrations}

        self.integrations = config.get('integrations')

        logger.info('Importing Integrations...')
        for integration_id, manifest in self.integrations.items():
            if self.integration_exists(integration_id):
                self.__import_integration(integration_id, manifest)
            else:
                self.integrations.pop(integration_id)
                config.set('integrations', self.integrations)
                logger.info(f"Removing {integration_id}")

    @property
    def imported_integrations(self):
        return [manifest for manifest in self.integrations.values()]

    @property
    def not_imported_integrations(self):
        return [manifest for _id, manifest in self.available_integrations.items() if _id not in self.integrations]

    def integration_imported(self, integration_id: str):
        return integration_id in self.imported_integration_modules

    def integration_exists(self, integration_id: str):
        return integration_id in self.available_integrations

    def remove_integration(self, integration_id: str):
        if self.integration_imported(integration_id):
            manifest = self.integrations.pop(integration_id)
            self.imported_integration_modules.pop(integration_id)
            config.set("integrations", self.integrations)
            return manifest
        raise RuntimeError("Integration not imported")

    def update_integration(self, integration_id: str, integration_config: typing.Dict):
        if self.integration_exists(integration_id):
            if not self.integration_imported(integration_id):
                manifest = self.get_integration_manifest(integration_id)
                if integration_config:
                    manifest["config"] = integration_config
            else:
                manifest = self.integrations[integration_id]
                if integration_config:
                    manifest["config"] = integration_config
            self.__import_integration(integration_id, manifest)
        else:
            raise RuntimeError("Integration does not exist")

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
        
    def get_integration_config(self, integration_id: str) -> typing.Dict:
        if self.integration_exists(integration_id):
            if self.integration_imported(integration_id) and "config" in self.integrations[integration_id]:
                return self.integrations[integration_id]["config"]
            else:
                return self.get_default_integration_config(integration_id)
        else:
            raise RuntimeError('Integration does not exist')

    def get_default_integration_config(self, integration_id: str) -> typing.Dict:
        if self.integration_exists(integration_id):
            manifest = self.get_integration_manifest(integration_id)
            if "config" in manifest:
                return manifest["config"]
            return {}
        else:
            raise RuntimeError('Integration does not exist')
        
    def get_integration_manifest(self, integration_id: str) -> typing.Dict:
        if self.integration_exists(integration_id):
            if self.integration_imported(integration_id):
                return self.integrations[integration_id]
            else:
                return self.get_default_integration_manifest(integration_id)
        else:
            raise RuntimeError('Integration does not exist')

    def get_default_integration_manifest(self, integration_id: str) -> typing.Dict:
        if self.integration_exists(integration_id):
            module = importlib.import_module(f'core.integrations.{integration_id}')
            return module.manifest()
        else:
            raise RuntimeError('Integration does not exist')
    
    def get_integration_module(self, integration_id: str):
        if self.integration_imported(integration_id):
            return self.imported_integration_modules[integration_id]
        else:
            raise RuntimeError("Integration is not imported")

    def __import_integration(self, integration_id: str, manifest: typing.Dict):
        if self.integration_exists(integration_id):
            logger.info(f"Importing {integration_id}")
            default_manifest = self.get_default_integration_manifest(integration_id)
            manifest = self.check_for_discrepancy(manifest, default_manifest)
            if "requirements" in manifest:
                requirements = manifest["requirements"]
                command = ["pip", "install"] + requirements
                try:
                    subprocess.check_output(command)
                except Exception as e:
                    raise RuntimeError(f"Failed to install integration requirements | {repr(e)}")
            if "config" in manifest:
                integration_config = manifest["config"]
                default_config = self.get_default_integration_config(integration_id)
                if not integration_config:
                    integration_config = default_config
                else:
                    integration_config = self.check_for_discrepancy(integration_config, default_config)
                manifest["config"] = integration_config
            else:
                integration_config = {}
            self.integrations[integration_id] = manifest
            config.set('integrations', self.integrations)
            try:
                module = importlib.import_module(f'core.integrations.{integration_id}')
                self.imported_integration_modules[integration_id] = module.build_integration(integration_config, self.ova)
            except Exception as e:
                logger.info(f'Failed to load {integration_id} | Exception {repr(e)}')
                # TODO
                # custom exception for this
                # in the future use it to extablish that integration is crashed
                # update flag in config and display on FE
                # can do same thing for integrations and even components
        else:
            raise RuntimeError('Integration does not exist')