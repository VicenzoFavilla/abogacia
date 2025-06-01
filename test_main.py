from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# TEST 1: Verificar que la API arranque correctamente
def test_root_redirect():
    response = client.get("/")
    assert response.status_code in (200, 307, 308)

# TEST 2: Crear una etiqueta nueva
def test_crear_etiqueta():
    data = {"nombre": "Importante"}
    response = client.post("/etiquetas/", json=data)
    assert response.status_code == 200 or response.status_code == 400  # Puede ya existir
    if response.status_code == 200:
        assert response.json()["nombre"] == "Importante"

# TEST 3: Obtener etiquetas
def test_listar_etiquetas():
    response = client.get("/etiquetas/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

#TEST 4: crea caso
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
