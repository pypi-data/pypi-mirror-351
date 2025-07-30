# Configure the injector
from typing import TypeVar, Type, Any

from injector import Module, singleton, provider

class injector_module(Module):
    binder_map: dict = {}
    interface = None
    to = None

    def set_mapping(self, binder_map: dict[Any, Any]):
        self.binder_map = binder_map

    def configure(self, binder):
        for item in self.binder_map.items():
            binder.bind(interface=item[0], to=item[1], scope=singleton)



