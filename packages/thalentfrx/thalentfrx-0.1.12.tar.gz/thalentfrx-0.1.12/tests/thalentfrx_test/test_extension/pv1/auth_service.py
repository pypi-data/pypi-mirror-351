from thalentfrx.core.services.AuthBaseService import AuthBaseService


class auth_service(AuthBaseService):

    def hello_world(self) -> str:
        return "Hello World! from Child"