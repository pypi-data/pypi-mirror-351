from thalentfrx.testclient import TestClient


def test_hello_world():
    from .app_pv1 import app

    client = TestClient(app)
    response = client.get("/hello_world")
    assert response.status_code == 200, response.text
    assert response.json() == "Hello World!"

def test_auth_router_test():
    from .app_pv1 import app

    client = TestClient(app)
    response = client.get("/v1/authtest/hello")
    assert response.status_code == 200, response.text
    assert response.json() == "Hello World! from auth_router"

def test_auth_router2_test():
    from .app_pv1 import app

    client = TestClient(app)
    response = client.get("v1/authtest/hellochild")
    assert response.status_code == 200, response.text
    assert response.json() == "Hello World! from Child"


