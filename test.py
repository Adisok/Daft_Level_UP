from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    resposne = client.get("/")
    assert resposne.status_code == 200
    assert resposne.json() == {"message": "Hello World"}
