from conftest import token, cantidad_lote
from database import SessionLocal
from modelos.producto import Producto


def venta(client, auth, datos, lineas):
    """lineas = [(producto_id, cantidad), ...]"""
    cuerpo = {
        "cliente_id": datos["cliente"],
        "total": 0,  
        "detalles": [{"producto_id": p, "cantidad": c, "precio_unitario": 0.01} for p, c in lineas],
    }
    return client.post("/api/v1/ventas/", json=cuerpo, headers=auth)


# ---------- AUTENTICACIÓN ----------

def test_login_da_token(client):
    assert len(token(client)) > 10

def test_login_con_clave_mala_da_401(client):
    r = client.post("/api/v1/auth/login", json={"usuario": "admin", "clave": "mala"})
    assert r.status_code == 401

def test_sin_token_no_deja_ver_nada(client):
    for ruta in ["/api/v1/lotes/", "/api/v1/ventas/", "/api/v1/productos/",
                 "/api/v1/clientes/", "/api/v1/usuarios/"]:
        assert client.get(ruta).status_code == 401, ruta


# ---------- USUARIOS ----------

def test_usuario_creado_por_api_puede_iniciar_sesion_y_no_expone_clave(client, auth):
    r = client.post("/api/v1/usuarios/", json={"username": "vend1", "password": "clave123", "rol": "vendedor"}, headers=auth)
    assert r.status_code == 200
    assert "password" not in r.json() and "password_hash" not in r.json()
    assert len(token(client, "vend1", "clave123")) > 10

def test_vendedor_no_puede_listar_usuarios(client, auth):
    client.post("/api/v1/usuarios/", json={"username": "vend1", "password": "clave123", "rol": "vendedor"}, headers=auth)
    h = {"Authorization": f"Bearer {token(client, 'vend1', 'clave123')}"}
    assert client.get("/api/v1/usuarios/", headers=h).status_code == 403


# ---------- LOTES ----------

def test_por_vencer_trae_solo_lotes_proximos(client, auth, nuevo_lote):
    nuevo_lote("PROXIMO", 10, 5)
    nuevo_lote("LEJANO", 400, 5)
    nuevo_lote("VENCIDO", -5, 5)
    r = client.get("/api/v1/lotes/por-vencer?dias=30", headers=auth)
    assert r.status_code == 200
    assert [l["numero_lote"] for l in r.json()] == ["PROXIMO"]

def test_lotes_por_producto_funciona(client, auth, datos, nuevo_lote):
    nuevo_lote("B", 200, 5)
    nuevo_lote("A", 100, 5)
    nuevo_lote("VENCIDO", -1, 5)
    r = client.get(f"/api/v1/lotes/producto/{datos['producto']}", headers=auth)
    assert r.status_code == 200
    assert [l["numero_lote"] for l in r.json()] == ["A", "B"]   # FEFO, sin vencidos

def test_no_permite_lote_repetido_para_el_mismo_producto(client, auth, datos):
    cuerpo = {"producto_id": datos["producto"], "proveedor_id": datos["proveedor"], "numero_lote": "X1",
              "fecha_vencimiento": "2030-01-01", "cantidad": 10, "precio_compra": 5}
    assert client.post("/api/v1/lotes/", json=cuerpo, headers=auth).status_code == 200
    assert client.post("/api/v1/lotes/", json=cuerpo, headers=auth).status_code == 400


# ---------- VENTAS: reglas de negocio ----------

def test_venta_descuenta_primero_del_lote_que_vence_antes(client, auth, datos, nuevo_lote):
    tarde = nuevo_lote("TARDE", 300, 10)
    pronto = nuevo_lote("PRONTO", 30, 5)
    r = venta(client, auth, datos, [(datos["producto"], 8)])
    assert r.status_code == 200, r.text
    assert cantidad_lote(pronto) == 0      
    assert cantidad_lote(tarde) == 7       

def test_no_vende_lotes_vencidos(client, auth, datos, nuevo_lote):
    vencido = nuevo_lote("VENCIDO", -3, 50)
    r = venta(client, auth, datos, [(datos["producto"], 1)])
    assert r.status_code == 400
    assert cantidad_lote(vencido) == 50

def test_stock_insuficiente_no_cambia_nada(client, auth, datos, nuevo_lote):
    lote = nuevo_lote("A", 30, 5)
    r = venta(client, auth, datos, [(datos["producto"], 6)])
    assert r.status_code == 400
    assert cantidad_lote(lote) == 5
    assert client.get("/api/v1/ventas/", headers=auth).json() == []

def test_mismo_producto_en_dos_lineas_no_supera_el_stock(client, auth, datos, nuevo_lote):
    lote = nuevo_lote("A", 30, 5)
    r = venta(client, auth, datos, [(datos["producto"], 3), (datos["producto"], 3)])
    assert r.status_code == 400
    assert cantidad_lote(lote) == 5

def test_venta_sin_productos_se_rechaza(client, auth, datos):
    r = venta(client, auth, datos, [])
    assert r.status_code == 400

def test_total_lo_calcula_el_servidor(client, auth, datos, nuevo_lote):
    nuevo_lote("A", 30, 20)
    r = venta(client, auth, datos, [(datos["producto"], 3)])    
    assert r.status_code == 200
    assert r.json()["total"] == 30.0                            

def test_stock_del_producto_se_mantiene_sincronizado(client, auth, datos, nuevo_lote):
    nuevo_lote("A", 30, 20)
    nuevo_lote("VENCIDO", -1, 99)
    venta(client, auth, datos, [(datos["producto"], 5)])
    db = SessionLocal()
    assert db.get(Producto, datos["producto"]).stock == 15      
    db.close()

def test_anular_venta_devuelve_el_stock(client, auth, datos, nuevo_lote):
    lote = nuevo_lote("A", 30, 10)
    r = venta(client, auth, datos, [(datos["producto"], 4)])
    assert cantidad_lote(lote) == 6
    assert client.delete(f"/api/v1/ventas/{r.json()['id']}", headers=auth).status_code == 200
    assert cantidad_lote(lote) == 10

def test_no_se_borra_un_lote_con_ventas(client, auth, datos, nuevo_lote):
    lote = nuevo_lote("A", 30, 10)
    venta(client, auth, datos, [(datos["producto"], 1)])
    assert client.delete(f"/api/v1/lotes/{lote}", headers=auth).status_code == 400


# ---------- REPORTE ----------

def test_reporte_valor_inventario_por_categoria(client, auth, nuevo_lote):
    nuevo_lote("A", 30, 10)        # vigente: 10 x L.10 = 100 (costo 10 x 6 = 60)
    nuevo_lote("VENCIDO", -1, 4)   # vencido: 4 x L.10 = 40
    r = client.get("/api/v1/categorias/reporte/valor-inventario", headers=auth)
    assert r.status_code == 200
    fila = r.json()["categorias"][0]
    assert fila["unidades_vigentes"] == 10
    assert fila["valor_venta"] == 100.0
    assert fila["valor_costo"] == 60.0
    assert fila["valor_vencido"] == 40.0