"""
Backend tests for Mergington High School Activities API using AAA pattern.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Arrange: Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Arrange: Reset activities to initial state before each test."""
    # Store original state
    original_activities = {
        name: {
            "description": details["description"],
            "schedule": details["schedule"],
            "max_participants": details["max_participants"],
            "participants": details["participants"].copy()
        }
        for name, details in activities.items()
    }
    yield
    # Restore original state after test
    for name, details in activities.items():
        details["participants"] = original_activities[name]["participants"].copy()


class TestGetActivities:
    """Test suite for GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """Arrange: Set up test client.
        Act: Send GET request to /activities.
        Assert: Response status is 200.
        """
        # Arrange is handled by fixtures

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client):
        """Arrange: Set up test client.
        Act: Send GET request to /activities.
        Assert: Response contains all expected activities.
        """
        # Arrange
        expected_activities = list(activities.keys())

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert len(data) == len(expected_activities)
        for activity_name in expected_activities:
            assert activity_name in data

    def test_get_activities_contains_required_fields(self, client):
        """Arrange: Set up test client.
        Act: Send GET request to /activities.
        Assert: Each activity has required fields.
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity_name, activity_details in data.items():
            for field in required_fields:
                assert field in activity_details, f"Missing {field} in {activity_name}"


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_adds_participant_successfully(self, client):
        """Arrange: Set up test client and new participant email.
        Act: Send POST request to signup endpoint.
        Assert: Participant is added and success message is returned.
        """
        # Arrange
        activity_name = "Chess Club"
        email = "test_student@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_duplicate_email_returns_400(self, client):
        """Arrange: Set up test client and existing participant.
        Act: Send POST request to signup with duplicate email.
        Assert: Request fails with 400 and participant count unchanged.
        """
        # Arrange
        activity_name = "Chess Club"
        email = activities[activity_name]["participants"][0]  # Use existing participant
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"
        assert len(activities[activity_name]["participants"]) == initial_count

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Arrange: Set up test client and invalid activity name.
        Act: Send POST request to signup for nonexistent activity.
        Assert: Request fails with 404.
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test_student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestRemoveParticipant:
    """Test suite for DELETE /activities/{activity_name}/signup endpoint."""

    def test_remove_participant_successfully(self, client):
        """Arrange: Set up test client and existing participant.
        Act: Send DELETE request to remove participant.
        Assert: Participant is removed and success message is returned.
        """
        # Arrange
        activity_name = "Chess Club"
        email = activities[activity_name]["participants"][0]  # Use existing participant
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1
        assert response.json()["message"] == f"Removed {email} from {activity_name}"

    def test_remove_nonexistent_participant_returns_404(self, client):
        """Arrange: Set up test client and nonexistent participant email.
        Act: Send DELETE request to remove nonexistent participant.
        Assert: Request fails with 404 and participant list unchanged.
        """
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
        assert len(activities[activity_name]["participants"]) == initial_count

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """Arrange: Set up test client and invalid activity name.
        Act: Send DELETE request for nonexistent activity.
        Assert: Request fails with 404.
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test_student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
