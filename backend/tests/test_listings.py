from fastapi.testclient import TestClient
from app.main import app  # Assuming your FastAPI app is defined in main.py or a similar file
import time

client = TestClient(app)

access_token = client.post("/api/auth/token?name=AnirudhMaiya&password=123456").json()["access_token"]
print(access_token)

# Test data for the /add and /update endpoints
test_listing_data = {
    "property_id": 1234,
    "title": "Test Property",
    "host": 456,
    "location": "Test Location",
    "price": 100.0,
    "rating": 4.5,
    "summary": "Test Summary",
    "booking_hostory": []
}

def test_sample_listing():
    # This fixture adds a sample listing to the database before each test and deletes it after the test
    result = client.post("/api/listings/add", json=test_listing_data, headers={"Authorization": "Bearer "+ access_token})
    assert result.status_code == 200
    return result.json()

def test_get_listings():
    response = client.get("/api/listings/list", headers={"Authorization": "Bearer "+ access_token})
    assert response.status_code == 200

def test_get_listings_by_user_id():
    user_id = test_listing_data["host"]
    response = client.get(f"/api/listings/list/{user_id}", headers={"Authorization": "Bearer "+ access_token})
    assert response.status_code == 200

def test_delete_listing():
    property_id = test_listing_data["property_id"]
    response = client.delete(f"/api/listings/delete/{property_id}", headers={"Authorization": "Bearer "+ access_token})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    time.sleep(10)
    # Verify that the listing is no longer present in the database
    response = client.get(f"/api/listings/list/{property_id}", headers={"Authorization": "Bearer "+ access_token})
    assert response.json() == '[]'
