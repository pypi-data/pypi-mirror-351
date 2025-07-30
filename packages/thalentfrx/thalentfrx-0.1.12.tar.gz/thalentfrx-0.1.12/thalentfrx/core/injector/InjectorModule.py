# Configure the injector
from typing import Type, TypeVar, Any

from injector import Module, singleton
# import importlib
#
# from thalentfrx.configs.Environment import get_environment_variables
#
# from thalentfrx.core.services.AuthBaseService import AuthBaseService


class InjectorModule(Module):
    binder_map: dict = {}
    interface = None
    to = None

    def set_mapping(self, binder_map: dict[Any, Any]):
        self.binder_map = binder_map

    def configure(self, binder):
        # env = get_environment_variables()
        # module = importlib.import_module(env.AUTH_SERVICE_MODULE_NAME)
        # class_ = getattr(module, env.AUTH_SERVICE_CLASS_NAME)
        # auth_service = class_()
        # auth_service = AuthService(repo=None)
        for item in self.binder_map.items():
            binder.bind(interface=item[0], to=item[1], scope=singleton)

        # binder.bind(interface=AuthBaseService, to=auth_service, scope=singleton)  # Bind the interface to a concrete implementation
