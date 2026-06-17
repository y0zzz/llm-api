import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os

os.environ["API_KEY"] = "test-key"
os.environ["CLOUDFLARE_ACCOUNT_ID"] = "fake-id"
os.environ["CLOUDFLARE_API_TOKEN"] = "fake-token"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from main import app

client = TestClient(app)
API_KEY = "test-key"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_generate_no_api_key():
    response = client.post("/generate", json={"prompt": "Hello!"})
    assert response.status_code == 403

def test_generate_invalid_api_key():
    response = client.post(
        "/generate",
        json={"prompt": "Hello!"},
        headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == 403

def test_list_models():
    with patch.dict("os.environ", {"API_KEY": API_KEY}):
        response = client.get("/models", headers={"X-API-Key": API_KEY})
        assert response.status_code == 200
        assert "available_models" in response.json()

def test_invalid_model():
    with patch.dict("os.environ", {"API_KEY": API_KEY}):
        response = client.post(
            "/generate",
            json={"prompt": "Hello!", "model": "invalid-model"},
            headers={"X-API-Key": API_KEY}
        )
        assert response.status_code == 400