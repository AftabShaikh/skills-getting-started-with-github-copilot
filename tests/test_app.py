
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: Reset activities before each test
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": []
        }
    })

def test_get_activities():
    # Arrange: Default state (fixture)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert response.json()["Chess Club"]["participants"] == []

def test_signup_success():
    # Arrange: Default state (fixture)
    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": "student1@example.com"})
    # Assert
    assert response.status_code == 200
    assert "student1@example.com" in activities["Chess Club"]["participants"]
    assert response.json()["message"] == "Signed up student1@example.com for Chess Club"

def test_signup_already_signed_up():
    # Arrange: Add participant
    activities["Chess Club"]["participants"].append("student1@example.com")
    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": "student1@example.com"})
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"

def test_signup_activity_not_found():
    # Arrange: No such activity
    # Act
    response = client.post("/activities/Nonexistent/signup", params={"email": "student2@example.com"})
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_get_root_redirect():
    # Arrange: None needed
    # Act
    response = client.get("/")
    # Assert
    assert response.status_code in (200, 307, 302)
    # Accepts direct HTML serving or redirect
    if response.status_code == 200:
        assert "index.html" in response.text or "<!DOCTYPE html>" in response.text
    else:
        assert response.headers["location"].endswith("/static/index.html")
    # Should redirect to /static/index.html or serve it
