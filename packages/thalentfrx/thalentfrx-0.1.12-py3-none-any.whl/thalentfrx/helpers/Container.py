from dependency_injector import containers, providers

from thalentfrx import ThalentFrx

class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    auth_service = providers.Singleton(
        ThalentFrx,
    )

