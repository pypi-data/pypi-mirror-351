from thalentfrx.core.services.AuthBaseService import AuthBaseService


class auth_service(AuthBaseService):
    def __init__(self) -> None:
        super().__init__()

    def hello_world(self) -> str:
        return "Hello World! from Child"

