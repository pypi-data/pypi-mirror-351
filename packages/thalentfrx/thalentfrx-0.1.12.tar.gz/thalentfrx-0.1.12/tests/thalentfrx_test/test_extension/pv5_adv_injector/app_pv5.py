from injector import Injector

from thalentfrx.core.endpoint.restapi import AuthRouter
from thalentfrx.core.services.AuthBaseService import AuthBaseService
from thalentfrx.core.injector.InjectorModule import InjectorModule
from thalentfrx import ThalentFrx
from thalentfrx.configs import Environment

from .auth_service import auth_service

app = ThalentFrx()
env = Environment.get_environment_variables()
app.environment_init(env=env)

inj_mod = InjectorModule()

auth_service = auth_service()
binder_map = {AuthBaseService: auth_service}
inj_mod.set_mapping(binder_map=binder_map)

inj = Injector([inj_mod])
service = inj.get(AuthBaseService)

AuthRouter.service = service

app.router_init(
    routers=[
        AuthRouter.AuthRouter
    ],
)


@app.get("/hello_world_5", response_model=str)
def hello_world():
    return "Hello World!"
