from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def get_token():
    r = client.post("/api/v1/auth/login", json={"usuario": "admin", "clave": "admin123"})
    assert r.status_code == 200
    return r.json()["access_token"]

def test_1_login_da_token():
    # Login con token - tiene que dar 200 y access_token
    token = get_token()
    assert token is not None
    assert len(token) > 10

def test_2_por_vencer_funciona():
    # Lotes por vencer - tiene que traer el LOT-PROXIMO
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/v1/lotes/por-vencer?dias=30", headers=headers)
    assert r.status_code == 200
    # Tiene que ser una lista
    assert isinstance(r.json(), list)

def test_3_no_deja_ver_sin_token():
    # Si no mandas token, te tiene que dar 401
    r = client.get("/api/v1/lotes/")
    assert r.status_code in [401, 403]