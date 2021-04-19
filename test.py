from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_read_main():
    resposne = client.get("/")
    assert resposne.status_code == 200
    assert resposne.json() == {"message": "Hello world!"}

def test_method():
    response = client.get("/method")
    assert response.status_code == 200
    assert response.json() == {"method": "GET"}