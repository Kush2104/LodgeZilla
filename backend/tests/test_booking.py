from fastapi.testclient import TestClient
import time

from app.main import app

client = TestClient(app)

access_token = client.post("/api/auth/token?name=AnirudhMaiya&password=123456").json()["access_token"]

test_listing_data = {
    "property_id": 123,
    "title": "TestProperty",
    "host": 1702359326,
    "location": "TestLocation",
    "price": 100.0,
    "rating": 4.5,
    "summary": "TestSummary",
    "booking_history": []
}

def test_sample_listing():
    # This fixture adds a sample listing to the database before each test and deletes it after the test
    result = client.post("/api/listings/add", json=test_listing_data, headers={"Authorization": "Bearer " + access_token})
    print(result)
    assert result.status_code == 200
    return result.json()

def test_search_properties():
    # Assuming you have some properties in your test database
    response = client.get("/api/bookings/search?destination=TestLocation&from_date=2023-01-01&to_date=2023-01-10", headers={"Authorization": "Bearer " + access_token})
    assert response.status_code == 200
    assert len(response.json()) > 0  # Adjust as needed

def test_reserve_property():
    # Assuming property_id exists in the test database
    response = client.post(
        "/api/bookings/reserve/123",
        json={"start_date": "2023-01-05", "end_date": "2023-01-10"},
        headers={"Authorization": "Bearer " + access_token}  # Replace with a valid access token
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data and data["message"] == "Reservation successful"
    assert "updated_property" in data and "updated_user" in data

    # Ensure the updated property has the expected booking history entry
    updated_property = data["updated_property"]
    assert "booking_history" in updated_property
    booking_entry = {"user_id": test_listing_data["host"], "start_date": "2023-01-05", "end_date": "2023-01-10"}
    assert booking_entry in updated_property["booking_history"]

    # Ensure the updated user has the expected trips field
    updated_user = data["updated_user"]
    assert "trips" in updated_user
    assert str(updated_property["property_id"]) in updated_user["trips"]

def test_delete_listing():
    property_id = test_listing_data["property_id"]
    response = client.delete(f"/api/listings/delete/{property_id}", headers={"Authorization": "Bearer "+ access_token})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    time.sleep(10)
    # Verify that the listing is no longer present in the database
    response = client.get(f"/api/listings/list/{property_id}", headers={"Authorization": "Bearer "+ access_token})
    assert response.json() == '[]'
