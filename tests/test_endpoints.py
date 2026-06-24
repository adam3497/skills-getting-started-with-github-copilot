import pytest


class TestGetActivities:
    """Test the GET /activities endpoint."""
    
    def test_get_all_activities_returns_correct_structure(self, client):
        """
        Arrange: Client with clean activities
        Act: GET /activities
        Assert: Returns all activities with correct structure
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert "Chess Club" in activities
        assert "Swimming Club" in activities
        assert "description" in activities["Chess Club"]
        assert "schedule" in activities["Chess Club"]
        assert "max_participants" in activities["Chess Club"]
        assert "participants" in activities["Chess Club"]
    
    def test_get_activities_shows_participant_count(self, client):
        """
        Arrange: Chess Club has 1 participant
        Act: GET /activities
        Assert: Participant count is correct
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert len(activities["Chess Club"]["participants"]) == 1
        assert "alice@mergington.edu" in activities["Chess Club"]["participants"]


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_student_success(self, client, sample_activity, sample_email):
        """
        Arrange: Clean activity with space available
        Act: POST signup with valid email and activity
        Assert: Returns 200 OK and adds student to participants
        """
        # Act
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        participants = activities_response.json()[sample_activity]["participants"]
        assert sample_email in participants
    
    def test_signup_duplicate_student_fails(self, client, sample_activity):
        """
        Arrange: Student alice@mergington.edu is already signed up for Chess Club
        Act: POST signup attempt with same email
        Assert: Returns 400 error for duplicate signup
        """
        # Act
        response = client.post(
            f"/activities/Chess Club/signup",
            params={"email": "alice@mergington.edu"}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_nonexistent_activity_fails(self, client, sample_email):
        """
        Arrange: Activity "Nonexistent Club" does not exist
        Act: POST signup to invalid activity
        Assert: Returns 404 Not Found
        """
        # Act
        response = client.post(
            f"/activities/Nonexistent Club/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_invalid_email_format_fails(self, client, sample_activity):
        """
        Arrange: Invalid email format provided
        Act: POST signup with invalid email
        Assert: Returns 400 error for invalid email
        """
        # Act
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": "not-an-email"}
        )
        
        # Assert
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    def test_signup_activity_at_max_capacity_fails(self, client):
        """
        Arrange: Chess Club has max_participants=2, currently has 1
        Act: Sign up 2 more students to fill capacity, then attempt 3rd
        Assert: 3rd signup returns 400 error
        """
        # Arrange: Fill first spot
        client.post(
            f"/activities/Chess Club/signup",
            params={"email": "bob@mergington.edu"}
        )
        
        # Act: Try to exceed capacity
        response = client.post(
            f"/activities/Chess Club/signup",
            params={"email": "charlie@mergington.edu"}
        )
        
        # Assert
        assert response.status_code == 400
        assert "capacity" in response.json()["detail"].lower()


class TestRemoveParticipant:
    """Test the DELETE /activities/{activity_name}/participants endpoint."""
    
    def test_remove_existing_participant_success(self, client):
        """
        Arrange: alice@mergington.edu is signed up for Chess Club
        Act: DELETE request to remove participant
        Assert: Returns 200 OK and removes from participants list
        """
        # Act
        response = client.delete(
            f"/activities/Chess Club/participants",
            params={"email": "alice@mergington.edu"}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        participants = activities_response.json()["Chess Club"]["participants"]
        assert "alice@mergington.edu" not in participants
    
    def test_remove_from_nonexistent_activity_fails(self, client, sample_email):
        """
        Arrange: Activity "Fake Club" does not exist
        Act: DELETE request for non-existent activity
        Assert: Returns 404 Not Found
        """
        # Act
        response = client.delete(
            f"/activities/Fake Club/participants",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_remove_nonexistent_participant_fails(self, client, sample_activity):
        """
        Arrange: nonexistent@mergington.edu is not signed up
        Act: DELETE request to remove non-existent participant
        Assert: Returns 404 Not Found
        """
        # Act
        response = client.delete(
            f"/activities/{sample_activity}/participants",
            params={"email": "nonexistent@mergington.edu"}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
