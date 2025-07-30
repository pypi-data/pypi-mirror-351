import os

from thalentfrx import ThalentFrx
from thalentfrx.configs import Environment

app = ThalentFrx()

def test_get_environment_value():
    # pass
    os.environ['ENV'] = 'test'
    test = os.getenv('ENV')
    assert test == 'test'

    env = Environment.get_environment_variables()
    assert env.ENV == 'test'
    assert env.DATABASE_NAME == 'dnb'
    app.environment_init(env=env)

    assert app.env.DATABASE_NAME == "dnb"
