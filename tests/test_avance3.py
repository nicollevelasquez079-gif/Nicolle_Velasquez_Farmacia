import sqlite3
from datetime import date
from servicios import respaldo


def vender(client, auth, datos, cantidad):
    return client.post("/api/v1/ventas/", headers=auth, json={
        "cliente_id": datos["cliente"],
        "detalles": [{"producto_id": datos["producto"], "cantidad": cantidad}]})


def test_csv_de_productos(client, auth):
    r = client.get("/api/v1/reportes/csv/productos", headers=auth)
    assert r.status_code == 200
    assert "attachment" in r.headers["content-disposition"]
    lineas = r.text.lstrip("\ufeff").splitlines()
    assert lineas[0].startswith("id;nombre")
    assert "Paracetamol" in r.text

def test_csv_no_exporta_usuarios_ni_cosas_raras(client, auth):
    assert client.get("/api/v1/reportes/csv/usuarios", headers=auth).status_code == 404
    assert client.get("/api/v1/reportes/csv/xyz", headers=auth).status_code == 404

def test_csv_exige_token(client):
    assert client.get("/api/v1/reportes/csv/productos").status_code == 401

def test_resumen_con_colecciones(client, auth, datos, nuevo_lote):
    nuevo_lote("A", 100, 20)
    nuevo_lote("POR-VENCER", 10, 5)
    nuevo_lote("VENCIDO", -2, 5)
    assert vender(client, auth, datos, 3).status_code == 200

    r = client.get("/api/v1/reportes/resumen", headers=auth)
    assert r.status_code == 200
    j = r.json()
    assert j["mas_vendidos"][0] == {"producto": "Paracetamol", "unidades": 3}
    assert j["ventas_por_dia"][date.today().isoformat()] == 30.0
    assert j["mejores_clientes"][0]["cliente"] == "Ana"
    assert j["lotes_por_estado"]["vencido"] == 1
    assert j["lotes_por_estado"]["por_vencer"] == 1
    assert j["productos_sin_ventas"] == []
    assert len(j["ultimas_ventas"]) == 1

def test_respaldo_en_hilo_crea_copia_valida(datos, tmp_path, monkeypatch):
    monkeypatch.setattr(respaldo, "CARPETA", str(tmp_path))
    hilo = respaldo.lanzar_respaldo()
    hilo.join(timeout=10)
    assert not hilo.is_alive()
    archivos = list(tmp_path.glob("farmacia_*.db"))
    assert len(archivos) == 1
    con = sqlite3.connect(archivos[0])
    assert con.execute("SELECT COUNT(*) FROM categorias").fetchone()[0] == 1
    con.close()

def test_solo_admin_puede_respaldar(client, auth):
    client.post("/api/v1/usuarios/", json={"username": "emp", "password": "clave123", "rol": "empleado"}, headers=auth)
    r = client.post("/api/v1/auth/login", json={"usuario": "emp", "clave": "clave123"})
    h = {"Authorization": "Bearer " + r.json()["access_token"]}
    assert client.get("/api/v1/respaldos/", headers=h).status_code == 403
    assert client.get("/api/v1/respaldos/", headers=auth).status_code == 200
