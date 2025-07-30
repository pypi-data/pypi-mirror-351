
from thalentfrx import ThalentFrx
from thalentfrx.configs import Environment
from .auth_router import auth_router

app = ThalentFrx()
env = Environment.get_environment_variables()
app.environment_init(env=env)

app.router_init(
    routers=[
        auth_router
    ],
)


@app.get("/hello_world_4", response_model=str)
def hello_world():
    return "Hello World!"
