from thalentfrx.testclient import TestClient


def test_hello_world():
    from .app_pv5 import app

    client = TestClient(app)
    response = client.get("/hello_world_5")
    assert response.status_code == 200, response.text
    assert response.json() == "Hello World!"


def test_hello_world_router():
    from .app_pv5 import app

    client = TestClient(app)
    response = client.get("/v1/auth/hello")
    assert response.status_code == 200, response.text
    assert response.json() == "Hello World! from AuthRouter"


# def test_hello_world_router2():
#     from .app_pv5 import app
#
#     client = TestClient(app)
#     response = client.get("/v1/auth/hellochild")
#     assert response.status_code == 200, response.text
#     assert response.json() == "Hello World! from Child"