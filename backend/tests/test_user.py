from fastapi.testclient import TestClient
import pytest
from urllib.parse import urlencode
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_login_for_access_token(client):
    # Test valid login
    response = client.post(
        "/api/auth/token?name=AnirudhMaiya&password=123456",
    )

    assert response.status_code == 200
    assert "access_token" in response.json()

    # Test invalid login
    response = client.post(
        "/api/auth/token?name=invalid_user&password=invalid_password",
    )
    assert response.status_code == 401
    assert "access_token" not in response.json()

    # Test missing username or password
    response = client.post("/api/auth/token", data={"name": "test_user"})
    assert response.status_code == 422

    response = client.post("/api/auth/token", data={"password": "test_password"})
    assert response.status_code == 422

def test_create_user(client):
    user_data = {
        "name": "test_user",
        "password": "test_password",
        "userType": "regular",
    }

    # Test user creation
    response = client.post("/api/auth/create", json=user_data)
    assert response.status_code == 200
    assert response.json()["id"] is not None

