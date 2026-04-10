"""
Backend tests for Mergington High School Activities API.
Uses AAA (Arrange-Act-Assert) pattern for clear test structure.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Arrange: Provide a test client for each test."""
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Assert: GET /activities returns all activities successfully."""
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) > 0

    def test_get_activities_includes_required_fields(self, client):
        """Assert: Each activity contains required fields."""
        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success_new_participant(self, client):
        """Assert: New participant successfully signs up for an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_duplicate_participant_rejected(self, client):
        """Assert: Duplicate signup is rejected with 400 error."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_activity_not_found(self, client):
        """Assert: Signup to non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_activity_full_rejected(self, client):
        """Assert: Signup to full activity is rejected with 400 error."""
        # Arrange
        # First, fill the Tennis Club (max 10, currently has 2)
        activity_name = "Tennis Club"
        for i in range(8):
            email = f"student{i}@mergington.edu"
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )

        # Try to sign up when activity is full
        email_overflow = "overflow@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email_overflow}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "full" in data["detail"].lower()


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup endpoint."""

    def test_unregister_success(self, client):
        """Assert: Participant successfully unregisters from activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Unregistered" in data["message"]

    def test_unregister_participant_not_enrolled(self, client):
        """Assert: Unregister for non-enrolled student returns 404."""
        # Arrange
        activity_name = "Chess Club"
        email = "notenrolled@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not signed up" in data["detail"].lower()

    def test_unregister_activity_not_found(self, client):
        """Assert: Unregister from non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_then_signup_again(self, client):
        """Assert: Can re-register after unregistering."""
        # Arrange
        activity_name = "Art Studio"
        email = "testartist@mergington.edu"

        # Signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200

        # Unregister
        response2 = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response2.status_code == 200

        # Act: Re-signup
        response3 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response3.status_code == 200
