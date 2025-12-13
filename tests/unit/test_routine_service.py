"""
Unit tests for RoutineService.

These tests mock the repository and embedding service layers.
"""

import pytest
from unittest.mock import Mock, patch
from src.services.routine_service import RoutineService
from src.models.routine import RoutineSearchResult


@pytest.fixture
def mock_routine_repository():
    """Mock routine repository."""
    return Mock()


@pytest.mark.unit
class TestRoutineServiceGetAllRoutines:
    """Tests for get_all_routines method."""

    def test_get_all_routines_success(
        self,
        mock_routine_repository,
        mock_embedding_service,
        sample_chroma_get_result_multiple
    ):
        """Should return all routines as RoutineSearchResult objects."""
        mock_routine_repository.get_all.return_value = sample_chroma_get_result_multiple
        service = RoutineService(mock_routine_repository, mock_embedding_service)

        result = service.get_all_routines()

        mock_routine_repository.get_all.assert_called_once()
        assert len(result) == 3
        assert all(isinstance(r, RoutineSearchResult) for r in result)
        assert result[0].id == "routine_1"
        assert result[0].text == "Practice C major scale"

    def test_get_all_routines_empty(self, mock_routine_repository, mock_embedding_service):
        """Should return empty list when no routines exist."""
        mock_routine_repository.get_all.return_value = {
            "ids": [],
            "documents": [],
            "metadatas": []
        }
        service = RoutineService(mock_routine_repository, mock_embedding_service)

        result = service.get_all_routines()

        assert result == []

    def test_get_all_routines_repository_error(
        self,
        mock_routine_repository,
        mock_embedding_service
    ):
        """Should propagate repository errors."""
        mock_routine_repository.get_all.side_effect = RuntimeError("Database error")
        service = RoutineService(mock_routine_repository, mock_embedding_service)

        with pytest.raises(RuntimeError, match="Database error"):
            service.get_all_routines()


@pytest.mark.unit
class TestRoutineServiceGetRoutinesByCategory:
    """Tests for get_routines_by_category method."""

    def test_get_by_category_success(self, mock_routine_repository, mock_embedding_service):
        """Should return routines filtered by category."""
        mock_routine_repository.get_by_category.return_value = {
            "ids": ["routine_1"],
            "documents": ["Practice scales"],
            "metadatas": [{"category": "technique", "tags": "scales", "state": "not_completed"}]
        }
        service = RoutineService(mock_routine_repository, mock_embedding_service)

        result = service.get_routines_by_category("technique")

        mock_routine_repository.get_by_category.assert_called_once_with("technique", None)
        assert len(result) == 1
        assert result[0].category == "technique"

    def test_get_by_category_with_state(self, mock_routine_repository, mock_embedding_service):
        """Should pass state filter to repository."""
        mock_routine_repository.get_by_category.return_value = {
            "ids": ["routine_1"],
            "documents": ["Practice scales"],
            "metadatas": [{"category": "technique", "tags": "scales", "state": "not_completed"}]
        }
        service = RoutineService(mock_routine_repository, mock_embedding_service)

        result = service.get_routines_by_category("technique", "not_completed")

        mock_routine_repository.get_by_category.assert_called_once_with("technique", "not_completed")
        assert len(result) == 1


@pytest.mark.unit
class TestRoutineServiceGetRandomRoutine:
    """Tests for get_random_routine_by_category method."""

    def test_get_random_routine_success(self, mock_routine_repository, mock_embedding_service):
        """Should return a random routine from the category."""
        mock_routine_repository.get_by_category.return_value = {
            "ids": ["routine_1", "routine_2", "routine_3"],
            "documents": ["Routine 1", "Routine 2", "Routine 3"],
            "metadatas": [
                {"category": "technique", "tags": "", "state": "not_completed"},
                {"category": "technique", "tags": "", "state": "not_completed"},
                {"category": "technique", "tags": "", "state": "not_completed"}
            ]
        }
        service = RoutineService(mock_routine_repository, mock_embedding_service)

        result = service.get_random_routine_by_category("technique")

        assert result is not None
        assert isinstance(result, RoutineSearchResult)
        assert result.category == "technique"

    def test_get_random_routine_no_results(self, mock_routine_repository, mock_embedding_service):
        """Should return None when no routines found."""
        mock_routine_repository.get_by_category.return_value = {
            "ids": [],
            "documents": [],
            "metadatas": []
        }
        service = RoutineService(mock_routine_repository, mock_embedding_service)

        result = service.get_random_routine_by_category("technique")

        assert result is None

    @patch('random.choice')
    def test_get_random_routine_randomness(
        self,
        mock_choice,
        mock_routine_repository,
        mock_embedding_service
    ):
        """Should use random.choice to select routine."""
        mock_routine_repository.get_by_category.return_value = {
            "ids": ["routine_1", "routine_2"],
            "documents": ["Routine 1", "Routine 2"],
            "metadatas": [
                {"category": "technique", "tags": "", "state": "not_completed"},
                {"category": "technique", "tags": "", "state": "not_completed"}
            ]
        }
        service = RoutineService(mock_routine_repository, mock_embedding_service)

        service.get_random_routine_by_category("technique")

        mock_choice.assert_called_once()
        call_args = mock_choice.call_args[0][0]
        assert len(call_args) == 2


@pytest.mark.unit
class TestRoutineServiceGetNotCompleted:
    """Tests for get_not_completed_routines method."""

    def test_get_not_completed_success(self, mock_routine_repository, mock_embedding_service):
        """Should return all not-completed routines."""
        mock_routine_repository.get_by_state.return_value = {
            "ids": ["routine_1", "routine_2"],
            "documents": ["Routine 1", "Routine 2"],
            "metadatas": [
                {"category": "technique", "tags": "", "state": "not_completed"},
                {"category": "chords", "tags": "", "state": "not_completed"}
            ]
        }
        service = RoutineService(mock_routine_repository, mock_embedding_service)

        result = service.get_not_completed_routines()

        mock_routine_repository.get_by_state.assert_called_once_with("not_completed")
        assert len(result) == 2
        assert all(r.state == "not_completed" for r in result)


@pytest.mark.unit
class TestRoutineServiceSearchRoutines:
    """Tests for search_routines method."""

    def test_search_routines_success(
        self,
        mock_routine_repository,
        mock_embedding_service,
        sample_chroma_query_result
    ):
        """Should perform semantic search successfully."""
        mock_embedding_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
        mock_routine_repository.search_by_embedding.return_value = sample_chroma_query_result
        service = RoutineService(mock_routine_repository, mock_embedding_service)

        result = service.search_routines("practice scales", top_n=5, min_score=0.3)

        mock_embedding_service.generate_embedding.assert_called_once_with("practice scales")
        mock_routine_repository.search_by_embedding.assert_called_once_with([0.1, 0.2, 0.3], 5)
        assert len(result) == 2
        assert all(isinstance(r, RoutineSearchResult) for r in result)

    def test_search_routines_filters_by_score(
        self,
        mock_routine_repository,
        mock_embedding_service
    ):
        """Should filter results by minimum score."""
        mock_embedding_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
        mock_routine_repository.search_by_embedding.return_value = {
            "ids": [["routine_1", "routine_2", "routine_3"]],
            "documents": [["Routine 1", "Routine 2", "Routine 3"]],
            "metadatas": [[
                {"category": "technique", "tags": "", "state": "not_completed"},
                {"category": "technique", "tags": "", "state": "not_completed"},
                {"category": "technique", "tags": "", "state": "not_completed"}
            ]],
            "distances": [[0.1, 0.25, 0.5]]  # Only first two should pass min_score=0.3
        }
        service = RoutineService(mock_routine_repository, mock_embedding_service)

        result = service.search_routines("practice scales", top_n=5, min_score=0.3)

        assert len(result) == 2
        assert result[0].score == 0.1
        assert result[1].score == 0.25

    def test_search_routines_invalid_query(
        self,
        mock_routine_repository,
        mock_embedding_service
    ):
        """Should raise ValueError for invalid query."""
        service = RoutineService(mock_routine_repository, mock_embedding_service)

        with pytest.raises(ValueError, match="Query must be a non-empty string"):
            service.search_routines("")

        with pytest.raises(ValueError, match="Query must be a non-empty string"):
            service.search_routines(None)

    def test_search_routines_invalid_top_n(
        self,
        mock_routine_repository,
        mock_embedding_service
    ):
        """Should raise ValueError for invalid top_n."""
        service = RoutineService(mock_routine_repository, mock_embedding_service)

        with pytest.raises(ValueError, match="top_n must be at least 1"):
            service.search_routines("practice scales", top_n=0)


@pytest.mark.unit
class TestRoutineServiceMarkCompleted:
    """Tests for mark_routine_completed method."""

    def test_mark_completed_success(self, mock_routine_repository, mock_embedding_service):
        """Should mark routine as completed."""
        mock_routine_repository.get_by_id.return_value = {
            "id": "routine_123",
            "document": "Practice scales",
            "metadata": {"category": "technique", "tags": "scales", "state": "not_completed"}
        }
        service = RoutineService(mock_routine_repository, mock_embedding_service)

        service.mark_routine_completed("routine_123")

        mock_routine_repository.get_by_id.assert_called_once_with("routine_123")
        mock_routine_repository.update_metadata.assert_called_once_with(
            "routine_123",
            {"category": "technique", "tags": "scales", "state": "completed"}
        )

    def test_mark_completed_routine_not_found(
        self,
        mock_routine_repository,
        mock_embedding_service
    ):
        """Should raise ValueError when routine not found."""
        mock_routine_repository.get_by_id.return_value = None
        service = RoutineService(mock_routine_repository, mock_embedding_service)

        with pytest.raises(ValueError, match="Routine routine_123 not found"):
            service.mark_routine_completed("routine_123")


@pytest.mark.unit
class TestRoutineServiceMarkNotCompleted:
    """Tests for mark_routine_not_completed method."""

    def test_mark_not_completed_success(
        self,
        mock_routine_repository,
        mock_embedding_service
    ):
        """Should mark routine as not completed."""
        mock_routine_repository.get_by_id.return_value = {
            "id": "routine_123",
            "document": "Practice scales",
            "metadata": {"category": "technique", "tags": "scales", "state": "completed"}
        }
        service = RoutineService(mock_routine_repository, mock_embedding_service)

        service.mark_routine_not_completed("routine_123")

        mock_routine_repository.get_by_id.assert_called_once_with("routine_123")
        mock_routine_repository.update_metadata.assert_called_once_with(
            "routine_123",
            {"category": "technique", "tags": "scales", "state": "not_completed"}
        )

    def test_mark_not_completed_routine_not_found(
        self,
        mock_routine_repository,
        mock_embedding_service
    ):
        """Should raise ValueError when routine not found."""
        mock_routine_repository.get_by_id.return_value = None
        service = RoutineService(mock_routine_repository, mock_embedding_service)

        with pytest.raises(ValueError, match="Routine routine_123 not found"):
            service.mark_routine_not_completed("routine_123")
