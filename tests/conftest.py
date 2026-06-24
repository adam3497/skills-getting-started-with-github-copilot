import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def clean_activities(monkeypatch):
    """
    Arrange: Provide a clean activities dictionary for testing.
    This fixture resets the global activities state before each test.
    """
    test_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 2,  # Small capacity for testing
            "participants": ["alice@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Swim training and water safety skills",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 3,
            "participants": []
        }
    }
    
    # Replace the global activities dict
    import src.app
    monkeypatch.setattr(src.app, "activities", test_activities)
    
    return test_activities


@pytest.fixture
def client(clean_activities):
    """
    Arrange: Provide a FastAPI TestClient with clean test data.
    """
    return TestClient(app)


@pytest.fixture
def sample_email():
    """Arrange: Provide a valid test email."""
    return "student@mergington.edu"


@pytest.fixture
def sample_activity():
    """Arrange: Provide a valid test activity name."""
    return "Swimming Club"
