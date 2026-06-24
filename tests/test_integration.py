import pytest


class TestSignupWorkflow:
    """Integration tests for complete signup workflows."""
    
    def test_full_signup_workflow(self, client, sample_activity, sample_email):
        """
        Arrange: Clean activity list
        Act: GET activities, then POST signup, then GET again
        Assert: Participant appears in updated activities list
        """
        # Arrange: Verify activity exists
        initial_response = client.get("/activities")
        assert sample_activity in initial_response.json()
        
        # Act: Sign up
        signup_response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert: Signup successful
        assert signup_response.status_code == 200
        
        # Act: Fetch updated activities
        updated_response = client.get("/activities")
        
        # Assert: Student appears in participants
        participants = updated_response.json()[sample_activity]["participants"]
        assert sample_email in participants


class TestRemovalWorkflow:
    """Integration tests for complete removal workflows."""
    
    def test_full_removal_workflow(self, client):
        """
        Arrange: alice@mergington.edu is signed up for Chess Club
        Act: Remove participant, then GET activities
        Assert: Participant is gone from list
        """
        # Arrange: Verify participant exists
        initial_response = client.get("/activities")
        assert "alice@mergington.edu" in initial_response.json()["Chess Club"]["participants"]
        
        # Act: Remove participant
        removal_response = client.delete(
            f"/activities/Chess Club/participants",
            params={"email": "alice@mergington.edu"}
        )
        
        # Assert: Removal successful
        assert removal_response.status_code == 200
        
        # Act: Fetch updated activities
        updated_response = client.get("/activities")
        
        # Assert: Participant is removed
        participants = updated_response.json()["Chess Club"]["participants"]
        assert "alice@mergington.edu" not in participants


class TestMultipleParticipants:
    """Integration tests for multiple participants in single activity."""
    
    def test_multiple_participants_signup(self, client, sample_activity):
        """
        Arrange: Clean activity with space available
        Act: Sign up two different students
        Assert: Both appear in participants list
        """
        # Act: Sign up first student
        client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": "bob@mergington.edu"}
        )
        
        # Act: Sign up second student
        client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": "charlie@mergington.edu"}
        )
        
        # Assert: Both students are listed
        response = client.get("/activities")
        participants = response.json()[sample_activity]["participants"]
        assert "bob@mergington.edu" in participants
        assert "charlie@mergington.edu" in participants
        assert len(participants) == 2
    
    def test_signup_and_removal_with_multiple_participants(self, client, sample_activity):
        """
        Arrange: Sign up three students
        Act: Remove middle participant
        Assert: Other two remain in list
        """
        # Arrange: Sign up three students
        emails = ["bob@mergington.edu", "charlie@mergington.edu", "diana@mergington.edu"]
        for email in emails:
            client.post(
                f"/activities/{sample_activity}/signup",
                params={"email": email}
            )
        
        # Act: Remove middle participant
        client.delete(
            f"/activities/{sample_activity}/participants",
            params={"email": "charlie@mergington.edu"}
        )
        
        # Assert: Others remain
        response = client.get("/activities")
        participants = response.json()[sample_activity]["participants"]
        assert "bob@mergington.edu" in participants
        assert "charlie@mergington.edu" not in participants
        assert "diana@mergington.edu" in participants
