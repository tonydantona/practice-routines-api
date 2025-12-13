"""
Integration tests for Flask API routes.

These tests use a test Flask client and mock the database layer.
"""

import pytest
from unittest.mock import Mock, patch
from flask import Flask
from src.api.routes import api_bp, init_routes
from src.services.routine_service import RoutineService


@pytest.fixture
def app(mock_routine_repository, mock_embedding_service):
    """Create a test Flask application."""
    app = Flask(__name__)

    # Create service with mocked dependencies
    routine_service = RoutineService(mock_routine_repository, mock_embedding_service)

    # Initialize routes
    init_routes(routine_service)

    # Register blueprint
    app.register_blueprint(api_bp)

    # Set testing mode
    app.config['TESTING'] = True

    return app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()


@pytest.mark.integration
class TestGetRandomRoutineEndpoint:
    """Tests for /api/get-random-routine-by-category-state endpoint."""

    def test_get_random_routine_success(self, client, mock_routine_repository):
        """Should return a random routine."""
        mock_routine_repository.get_by_category.return_value = {
            "ids": ["routine_1"],
            "documents": ["Practice C major scale"],
            "metadatas": [{"category": "technique", "tags": "scales", "state": "not_completed"}]
        }

        response = client.get('/api/get-random-routine-by-category-state?category=technique')

        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Practice C major scale"

    def test_get_random_routine_missing_category(self, client):
        """Should return 400 when category is missing."""
        response = client.get('/api/get-random-routine-by-category-state')

        assert response.status_code == 400
        data = response.get_json()
        assert "Category parameter is required" in data["error"]

    def test_get_random_routine_not_found(self, client, mock_routine_repository):
        """Should return 404 when no routines found."""
        mock_routine_repository.get_by_category.return_value = {
            "ids": [],
            "documents": [],
            "metadatas": []
        }

        response = client.get('/api/get-random-routine-by-category-state?category=technique')

        assert response.status_code == 404
        data = response.get_json()
        assert "No routines found" in data["error"]

    def test_get_random_routine_with_state_filter(self, client, mock_routine_repository):
        """Should pass state filter to service."""
        mock_routine_repository.get_by_category.return_value = {
            "ids": ["routine_1"],
            "documents": ["Practice scales"],
            "metadatas": [{"category": "technique", "tags": "scales", "state": "completed"}]
        }

        response = client.get('/api/get-random-routine-by-category-state?category=technique&state=completed')

        assert response.status_code == 200
        mock_routine_repository.get_by_category.assert_called_once_with("technique", "completed")

    def test_get_random_routine_state_all(self, client, mock_routine_repository):
        """Should pass None to service when state is 'all'."""
        mock_routine_repository.get_by_category.return_value = {
            "ids": ["routine_1"],
            "documents": ["Practice scales"],
            "metadatas": [{"category": "technique", "tags": "scales", "state": "not_completed"}]
        }

        response = client.get('/api/get-random-routine-by-category-state?category=technique&state=all')

        assert response.status_code == 200
        mock_routine_repository.get_by_category.assert_called_once_with("technique", None)


@pytest.mark.integration
class TestGetAllRoutinesEndpoint:
    """Tests for /api/routines endpoint."""

    def test_get_all_routines_success(self, client, mock_routine_repository):
        """Should return all routines."""
        mock_routine_repository.get_all.return_value = {
            "ids": ["routine_1", "routine_2"],
            "documents": ["Routine 1", "Routine 2"],
            "metadatas": [
                {"category": "technique", "tags": "scales", "state": "not_completed"},
                {"category": "chords", "tags": "progressions", "state": "completed"}
            ]
        }

        response = client.get('/api/routines')

        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 2
        assert len(data["routines"]) == 2

    def test_get_routines_by_category(self, client, mock_routine_repository):
        """Should filter routines by category."""
        mock_routine_repository.get_by_category.return_value = {
            "ids": ["routine_1"],
            "documents": ["Practice scales"],
            "metadatas": [{"category": "technique", "tags": "scales", "state": "not_completed"}]
        }

        response = client.get('/api/routines?category=technique')

        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 1
        mock_routine_repository.get_by_category.assert_called_once_with("technique", None)

    def test_get_routines_by_category_and_state(self, client, mock_routine_repository):
        """Should filter routines by category and state."""
        mock_routine_repository.get_by_category.return_value = {
            "ids": ["routine_1"],
            "documents": ["Practice scales"],
            "metadatas": [{"category": "technique", "tags": "scales", "state": "not_completed"}]
        }

        response = client.get('/api/routines?category=technique&state=not_completed')

        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 1
        mock_routine_repository.get_by_category.assert_called_once_with("technique", "not_completed")

    def test_get_not_completed_routines(self, client, mock_routine_repository):
        """Should return not-completed routines when state filter is used alone."""
        mock_routine_repository.get_by_state.return_value = {
            "ids": ["routine_1"],
            "documents": ["Practice scales"],
            "metadatas": [{"category": "technique", "tags": "scales", "state": "not_completed"}]
        }

        response = client.get('/api/routines?state=not_completed')

        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 1
        mock_routine_repository.get_by_state.assert_called_once_with("not_completed")


@pytest.mark.integration
class TestSearchRoutinesEndpoint:
    """Tests for /api/routines/search endpoint."""

    def test_search_routines_success(
        self,
        client,
        mock_routine_repository,
        mock_embedding_service
    ):
        """Should perform semantic search."""
        mock_embedding_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
        mock_routine_repository.search_by_embedding.return_value = {
            "ids": [["routine_1"]],
            "documents": [["Practice scales"]],
            "metadatas": [[{"category": "technique", "tags": "scales", "state": "not_completed"}]],
            "distances": [[0.15]]
        }

        response = client.get('/api/routines/search?query=practice scales')

        assert response.status_code == 200
        data = response.get_json()
        assert data["query"] == "practice scales"
        assert data["count"] == 1
        assert len(data["routines"]) == 1

    def test_search_routines_missing_query(self, client):
        """Should return 400 when query is missing."""
        response = client.get('/api/routines/search')

        assert response.status_code == 400
        data = response.get_json()
        assert "Query parameter is required" in data["error"]

    def test_search_routines_with_params(
        self,
        client,
        mock_routine_repository,
        mock_embedding_service
    ):
        """Should accept top_n and min_score parameters."""
        mock_embedding_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
        mock_routine_repository.search_by_embedding.return_value = {
            "ids": [["routine_1"]],
            "documents": [["Practice scales"]],
            "metadatas": [[{"category": "technique", "tags": "scales", "state": "not_completed"}]],
            "distances": [[0.15]]
        }

        response = client.get('/api/routines/search?query=scales&top_n=10&min_score=0.5')

        assert response.status_code == 200
        # Verify that the service was called with the correct parameters
        mock_embedding_service.generate_embedding.assert_called_once_with("scales")


@pytest.mark.integration
class TestMarkRoutineCompletedEndpoint:
    """Tests for /api/routines/<routine_id>/complete endpoint."""

    def test_mark_routine_completed_success(self, client, mock_routine_repository):
        """Should mark routine as completed."""
        mock_routine_repository.get_by_id.return_value = {
            "id": "routine_123",
            "document": "Practice scales",
            "metadata": {"category": "technique", "tags": "scales", "state": "not_completed"}
        }

        response = client.put('/api/routines/routine_123/complete')

        assert response.status_code == 200
        data = response.get_json()
        assert "marked as completed" in data["message"]
        mock_routine_repository.update_metadata.assert_called_once()

    def test_mark_routine_completed_not_found(self, client, mock_routine_repository):
        """Should return 404 when routine not found."""
        mock_routine_repository.get_by_id.return_value = None

        response = client.put('/api/routines/nonexistent/complete')

        assert response.status_code == 404
        data = response.get_json()
        assert "not found" in data["error"]


@pytest.mark.integration
class TestMarkRoutineNotCompletedEndpoint:
    """Tests for /api/routines/<routine_id>/uncomplete endpoint."""

    def test_mark_routine_not_completed_success(self, client, mock_routine_repository):
        """Should mark routine as not completed."""
        mock_routine_repository.get_by_id.return_value = {
            "id": "routine_123",
            "document": "Practice scales",
            "metadata": {"category": "technique", "tags": "scales", "state": "completed"}
        }

        response = client.put('/api/routines/routine_123/uncomplete')

        assert response.status_code == 200
        data = response.get_json()
        assert "marked as not completed" in data["message"]
        mock_routine_repository.update_metadata.assert_called_once()

    def test_mark_routine_not_completed_not_found(self, client, mock_routine_repository):
        """Should return 404 when routine not found."""
        mock_routine_repository.get_by_id.return_value = None

        response = client.put('/api/routines/nonexistent/uncomplete')

        assert response.status_code == 404
        data = response.get_json()
        assert "not found" in data["error"]


@pytest.mark.integration
class TestErrorHandling:
    """Tests for error handling across API endpoints."""

    def test_internal_server_error(self, client, mock_routine_repository):
        """Should return 500 on internal errors."""
        mock_routine_repository.get_all.side_effect = Exception("Database error")

        response = client.get('/api/routines')

        assert response.status_code == 500
        data = response.get_json()
        assert "Internal server error" in data["error"]

    def test_value_error_returns_400(self, client, mock_routine_repository):
        """Should return 400 for ValueError exceptions."""
        mock_routine_repository.get_by_category.side_effect = ValueError("Invalid category")

        response = client.get('/api/routines?category=technique')

        assert response.status_code == 400
        data = response.get_json()
        assert "Invalid category" in data["error"]
