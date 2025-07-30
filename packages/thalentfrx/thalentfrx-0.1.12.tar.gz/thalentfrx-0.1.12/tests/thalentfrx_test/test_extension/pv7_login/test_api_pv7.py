from thalentfrx.testclient import TestClient


def test_hello_world():
    from .app_pv7 import app

    client = TestClient(app)
    response = client.get("/hello_world_7")
    assert response.status_code == 200, response.text
    assert response.json() == "Hello World!"


def test_auth_router_login():
    from .app_pv7 import app
    from thalentfrx.helpers.fastapi.AuthHelper import AuthHelper

    client = TestClient(app)
    data = {
        "username": "test",
        "password": "test",
        "is_remember": True,
    }
    response = client.post("/v1/auth/login", data=data)
    assert response.status_code == 200, response.text

    access_token = response.json()["access_token"]
    identity, scope = AuthHelper.token_validate(access_token)

    assert identity == "test"


def test_auth_router_refresh_token():
    from .app_pv7 import app
    from thalentfrx.helpers.fastapi.AuthHelper import AuthHelper

    client = TestClient(app)
    data = {
        "username": "test",
        "password": "test",
        "is_remember": True,
    }
    response = client.post("/v1/auth/login", data=data)
    assert response.status_code == 200, response.text

    refresh_token = response.json()["refresh_token"]

    headers = {
        "Authorization": f"Bearer {refresh_token}",
    }
    response = client.post("/v1/auth/token/refresh", headers=headers)
    assert response.status_code == 200, response.text
    access_token = response.json()["access_token"]
    identity, scope = AuthHelper.token_validate(access_token)

    assert identity == "test"


def test_auth_router_me():
    from .app_pv7 import app
    from thalentfrx.helpers.fastapi.AuthHelper import AuthHelper

    client = TestClient(app)
    data = {
        "username": "test",
        "password": "test",
        "is_remember": True,
    }
    response = client.post("/v1/auth/login", data=data)
    assert response.status_code == 200, response.text

    refresh_token = response.json()["refresh_token"]

    headers = {
        "Authorization": f"Bearer {refresh_token}",
    }
    response = client.post("/v1/auth/me", headers=headers)
    assert response.status_code == 200, response.text
    username = response.json()["username"]
    assert username == "test"


def test_auth_router_token():
    from .app_pv7 import app
    from thalentfrx.helpers.fastapi.AuthHelper import AuthHelper

    client = TestClient(app)
    data = {
        "username": "test",
        "password": "test",
        "is_remember": True,
    }
    response = client.post("/v1/auth/login", data=data)
    assert response.status_code == 200, response.text

    refresh_token = response.json()["refresh_token"]

    headers = {
        "Authorization": f"Bearer {refresh_token}",
    }
    response = client.post("/v1/auth/token", headers=headers)
    assert response.status_code == 200, response.text
    # assert response.json() == {}
    token = response.json()["token"]
    assert token == refresh_token

def test_auth_router_validate():
    from .app_pv7 import app
    from thalentfrx.helpers.fastapi.AuthHelper import AuthHelper

    client = TestClient(app)
    data = {
        "username": "test",
        "password": "test",
        "is_remember": True,
    }
    response = client.post("/v1/auth/login", data=data)
    assert response.status_code == 200, response.text

    refresh_token = response.json()["refresh_token"]

    headers = {
        "Authorization": f"Bearer {refresh_token}",
    }
    response = client.post("/v1/auth/token/validate", headers=headers)
    assert response.status_code == 200, response.text
    # assert response.json() == {}
    assert response.json()["identity"] == "test"
    assert response.json()["is_valid"] == True