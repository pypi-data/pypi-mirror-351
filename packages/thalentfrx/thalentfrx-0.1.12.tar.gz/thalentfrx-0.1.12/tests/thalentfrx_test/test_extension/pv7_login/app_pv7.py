from thalentfrx import ThalentFrx
from thalentfrx.configs import Environment
from thalentfrx.core.endpoint.restapi import AuthRouter
from .auth_service import auth_service

app = ThalentFrx()
env = Environment.get_environment_variables()
app.environment_init(env=env)

auth_service = auth_service()
AuthRouter.service = auth_service

app.router_init(
    routers=[
        AuthRouter.AuthRouter
    ],
)


@app.get("/hello_world_7", response_model=str)
def hello_world():
    return "Hello World!"
