from thalentfrx.testclient import TestClient


def test_hello_world():
    from .app_pv2 import app

    client = TestClient(app)
    response = client.get("/hello_world_2")
    assert response.status_code == 200, response.text
    assert response.json() == "Hello World!"


def test_hello_world_router():
    from .app_pv2 import app

    client = TestClient(app)
    response = client.get("/v1/authtestinjector/hello")
    assert response.status_code == 200, response.text
    assert response.json() == "Hello World! from auth_router"


def test_hello_world_router2():
    from .app_pv2 import app

    client = TestClient(app)
    response = client.get("/v1/authtestinjector/hellochild")
    assert response.status_code == 200, response.text
    assert response.json() == "Hello World! from Child"