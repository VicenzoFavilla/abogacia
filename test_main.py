from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# ---------------------- TEST 1: Redirección raíz ----------------------
def test_root_redirect():
    response = client.get("/")
    assert response.status_code in (200, 307, 308)

# ---------------------- TEST 2: Crear etiqueta ----------------------
def test_crear_etiqueta():
    data = {"nombre": "Importante"}
    response = client.post("/etiquetas/", json=data)
    assert response.status_code == 200 or response.status_code == 400
    if response.status_code == 200:
        assert response.json()["nombre"] == "Importante"

# ---------------------- TEST 3: Listar etiquetas ----------------------
def test_listar_etiquetas():
    response = client.get("/etiquetas/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# ---------------------- TEST 4: Crear caso ----------------------
def test_crear_caso():
    data = {
        "titulo": "Demanda laboral",
        "descripcion": "Juicio por indemnización",
        "tipo": "Laboral",
        "estado": "Activo"
    }
    response = client.post("/casos/", json=data)
    assert response.status_code == 200
    assert "id" in response.json()

# ---------------------- FUNCIONES AUXILIARES ----------------------
def crear_caso():
    data = {
        "titulo": "Caso de prueba",
        "descripcion": "Descripción del caso",
        "tipo": "Civil",
        "estado": "Activo"
    }
    response = client.post("/casos/", json=data)
    return response.json()["id"]

def crear_documento(caso_id: int):
    files = {"archivo": ("test.txt", b"Contenido de prueba")}
    data = {"nombre": "Documento Test", "caso_id": caso_id}
    response = client.post("/documentos/", data=data, files=files)
    return response.json()["documento_id"]  # ✅ clave correcta


# ---------------------- TEST 5: Subir documento ----------------------
def test_subir_documento():
    caso_id = crear_caso()
    doc_id = crear_documento(caso_id)
    assert isinstance(doc_id, int)

# ---------------------- TEST 6: Listar documentos ----------------------
def test_listar_documentos():
    response = client.get("/documentos/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# ---------------------- TEST 7: Descargar documento ----------------------
def test_descargar_documento():
    caso_id = crear_caso()
    doc_id = crear_documento(caso_id)
    response = client.get(f"/documentos/{doc_id}/descargar")
    assert response.status_code == 200
    content_type = response.headers["content-type"]
    assert content_type.startswith("application/octet-stream") or content_type.startswith("text/plain")

# ---------------------- TEST 8: Crear anotación ----------------------
def test_crear_anotacion():
    caso_id = crear_caso()
    doc_id = crear_documento(caso_id)
    data = {
        "texto": "Primera anotación de prueba",
        "autor": "TestUser"
    }
    response = client.post(f"/documentos/{doc_id}/anotaciones", json=data)
    assert response.status_code == 200
    json = response.json()
    assert json["texto"] == "Primera anotación de prueba"
    assert json["autor"] == "TestUser"
    assert json["documento_id"] == doc_id

# ---------------------- TEST 9: Listar anotaciones ----------------------
def test_listar_anotaciones():
    caso_id = crear_caso()
    doc_id = crear_documento(caso_id)
    for i in range(2):
        client.post(f"/documentos/{doc_id}/anotaciones", json={
            "texto": f"Nota #{i}",
            "autor": "Tester"
        })
    response = client.get(f"/documentos/{doc_id}/anotaciones")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 2
