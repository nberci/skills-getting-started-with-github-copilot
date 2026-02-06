import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        # Check that Basketball Club exists (from fixture)
        assert "Basketball Club" in data

    def test_get_activities_has_correct_structure(self, client):
        """Test that activities have the correct structure."""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Basketball Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_get_activities_contains_initial_participants(self, client):
        """Test that activities contain their initial participants."""
        response = client.get("/activities")
        data = response.json()
        
        # Basketball Club should have alex@mergington.edu
        assert "alex@mergington.edu" in data["Basketball Club"]["participants"]


class TestSignUp:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity."""
        email = "newemail@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
        
        # Verify participant was added
        verify = client.get("/activities")
        assert email in verify.json()[activity]["participants"]

    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test that duplicate signups are rejected."""
        email = "alex@mergington.edu"  # Already signed up for Basketball Club
        activity = "Basketball Club"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for a non-existent activity."""
        email = "newemail@mergington.edu"
        activity = "NonExistent Activity"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple activities."""
        email = "student@mergington.edu"
        
        # Sign up for Basketball Club
        response1 = client.post(
            "/activities/Basketball Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for Soccer Team
        response2 = client.post(
            "/activities/Soccer Team/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify in both activities
        verify = client.get("/activities")
        assert email in verify.json()["Basketball Club"]["participants"]
        assert email in verify.json()["Soccer Team"]["participants"]


class TestRemoveParticipant:
    """Tests for the DELETE /activities/{activity_name}/remove endpoint."""

    def test_remove_participant_successful(self, client, reset_activities):
        """Test successful removal of a participant."""
        email = "alex@mergington.edu"
        activity = "Basketball Club"
        
        # Verify participant is there initially
        verify_before = client.get("/activities")
        assert email in verify_before.json()[activity]["participants"]
        
        # Remove participant
        response = client.delete(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
        
        # Verify participant was removed
        verify_after = client.get("/activities")
        assert email not in verify_after.json()[activity]["participants"]

    def test_remove_nonexistent_participant(self, client, reset_activities):
        """Test removing a participant who isn't signed up."""
        email = "nobody@mergington.edu"
        activity = "Basketball Club"
        
        response = client.delete(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]

    def test_remove_from_nonexistent_activity(self, client, reset_activities):
        """Test removing from a non-existent activity."""
        email = "alex@mergington.edu"
        activity = "NonExistent Activity"
        
        response = client.delete(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_remove_and_readd(self, client, reset_activities):
        """Test removing a participant and re-adding them."""
        email = "test@mergington.edu"
        activity = "Drama Club"
        
        # Add participant
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Remove participant
        response2 = client.delete(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Re-add participant
        response3 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
        
        # Verify participant is there
        verify = client.get("/activities")
        assert email in verify.json()[activity]["participants"]


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["Location"]
