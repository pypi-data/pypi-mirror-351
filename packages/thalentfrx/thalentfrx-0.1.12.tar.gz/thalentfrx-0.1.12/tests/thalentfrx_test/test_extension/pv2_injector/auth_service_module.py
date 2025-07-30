# Configure the injector
from injector import Module, singleton

from thalentfrx.core.services.AuthBaseService import AuthBaseService
from .auth_service import auth_service

class auth_service_module(Module):
    def configure(self, binder):
        service = auth_service()
        binder.bind(interface=AuthBaseService, to=service, scope=singleton)  # Bind the interface to a concrete implementation

