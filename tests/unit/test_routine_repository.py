"""
Unit tests for RoutineRepository.

These tests mock ChromaDB and test the repository layer in isolation.
"""

import pytest
from unittest.mock import Mock
from src.repositories.routine_repository import RoutineRepository


@pytest.mark.unit
class TestRoutineRepositoryGetAll:
    """Tests for get_all method."""

    def test_get_all_success(self, mock_chroma_collection, sample_chroma_get_result_multiple):
        """Should return all routines from the database."""
        mock_chroma_collection.get.return_value = sample_chroma_get_result_multiple
        repo = RoutineRepository(mock_chroma_collection)

        result = repo.get_all()

        mock_chroma_collection.get.assert_called_once_with()
        assert result == sample_chroma_get_result_multiple
        assert len(result["ids"]) == 3

    def test_get_all_empty(self, mock_chroma_collection):
        """Should return empty results when no routines exist."""
        empty_result = {"ids": [], "documents": [], "metadatas": []}
        mock_chroma_collection.get.return_value = empty_result
        repo = RoutineRepository(mock_chroma_collection)

        result = repo.get_all()

        assert result == empty_result
        assert len(result["ids"]) == 0

    def test_get_all_database_error(self, mock_chroma_collection):
        """Should raise RuntimeError when database query fails."""
        mock_chroma_collection.get.side_effect = Exception("Database error")
        repo = RoutineRepository(mock_chroma_collection)

        with pytest.raises(RuntimeError, match="Failed to fetch routines"):
            repo.get_all()


@pytest.mark.unit
class TestRoutineRepositoryGetByCategory:
    """Tests for get_by_category method."""

    def test_get_by_category_success(self, mock_chroma_collection):
        """Should return routines filtered by category."""
        expected_result = {
            "ids": ["routine_1"],
            "documents": ["Practice scales"],
            "metadatas": [{"category": "technique", "tags": "scales", "state": "not_completed"}]
        }
        mock_chroma_collection.get.return_value = expected_result
        repo = RoutineRepository(mock_chroma_collection)

        result = repo.get_by_category("technique")

        mock_chroma_collection.get.assert_called_once_with(where={"category": "technique"})
        assert result == expected_result

    def test_get_by_category_with_state(self, mock_chroma_collection):
        """Should return routines filtered by category and state."""
        expected_result = {
            "ids": ["routine_1"],
            "documents": ["Practice scales"],
            "metadatas": [{"category": "technique", "tags": "scales", "state": "not_completed"}]
        }
        mock_chroma_collection.get.return_value = expected_result
        repo = RoutineRepository(mock_chroma_collection)

        result = repo.get_by_category("technique", "not_completed")

        mock_chroma_collection.get.assert_called_once_with(
            where={"$and": [{"category": "technique"}, {"state": "not_completed"}]}
        )
        assert result == expected_result

    def test_get_by_category_invalid_category(self, mock_chroma_collection):
        """Should raise ValueError when category is invalid."""
        repo = RoutineRepository(mock_chroma_collection)

        with pytest.raises(ValueError, match="Category must be a non-empty string"):
            repo.get_by_category("")

        with pytest.raises(ValueError, match="Category must be a non-empty string"):
            repo.get_by_category(None)

    def test_get_by_category_database_error(self, mock_chroma_collection):
        """Should raise RuntimeError when database query fails."""
        mock_chroma_collection.get.side_effect = Exception("Database error")
        repo = RoutineRepository(mock_chroma_collection)

        with pytest.raises(RuntimeError, match="Database query failed"):
            repo.get_by_category("technique")


@pytest.mark.unit
class TestRoutineRepositoryGetByState:
    """Tests for get_by_state method."""

    def test_get_by_state_success(self, mock_chroma_collection):
        """Should return routines filtered by state."""
        expected_result = {
            "ids": ["routine_1", "routine_2"],
            "documents": ["Practice scales", "Practice chords"],
            "metadatas": [
                {"category": "technique", "tags": "scales", "state": "not_completed"},
                {"category": "chords", "tags": "progressions", "state": "not_completed"}
            ]
        }
        mock_chroma_collection.get.return_value = expected_result
        repo = RoutineRepository(mock_chroma_collection)

        result = repo.get_by_state("not_completed")

        mock_chroma_collection.get.assert_called_once_with(where={"state": "not_completed"})
        assert result == expected_result

    def test_get_by_state_invalid_state(self, mock_chroma_collection):
        """Should raise ValueError when state is invalid."""
        repo = RoutineRepository(mock_chroma_collection)

        with pytest.raises(ValueError, match="State must be a non-empty string"):
            repo.get_by_state("")

        with pytest.raises(ValueError, match="State must be a non-empty string"):
            repo.get_by_state(None)


@pytest.mark.unit
class TestRoutineRepositorySearchByEmbedding:
    """Tests for search_by_embedding method."""

    def test_search_by_embedding_success(self, mock_chroma_collection, sample_embedding, sample_chroma_query_result):
        """Should perform semantic search successfully."""
        mock_chroma_collection.query.return_value = sample_chroma_query_result
        repo = RoutineRepository(mock_chroma_collection)

        result = repo.search_by_embedding(sample_embedding, top_n=5)

        mock_chroma_collection.query.assert_called_once_with(
            query_embeddings=[sample_embedding],
            n_results=5,
            where=None
        )
        assert result == sample_chroma_query_result

    def test_search_by_embedding_with_filters(self, mock_chroma_collection, sample_embedding):
        """Should apply metadata filters when provided."""
        repo = RoutineRepository(mock_chroma_collection)
        where_filter = {"category": "technique"}

        repo.search_by_embedding(sample_embedding, top_n=3, where=where_filter)

        mock_chroma_collection.query.assert_called_once_with(
            query_embeddings=[sample_embedding],
            n_results=3,
            where=where_filter
        )

    def test_search_by_embedding_empty_embedding(self, mock_chroma_collection):
        """Should raise ValueError when embedding is empty."""
        repo = RoutineRepository(mock_chroma_collection)

        with pytest.raises(ValueError, match="Query embedding cannot be empty"):
            repo.search_by_embedding([])

    def test_search_by_embedding_invalid_top_n(self, mock_chroma_collection, sample_embedding):
        """Should raise ValueError when top_n is less than 1."""
        repo = RoutineRepository(mock_chroma_collection)

        with pytest.raises(ValueError, match="top_n must be at least 1"):
            repo.search_by_embedding(sample_embedding, top_n=0)


@pytest.mark.unit
class TestRoutineRepositoryUpdateMetadata:
    """Tests for update_metadata method."""

    def test_update_metadata_success(self, mock_chroma_collection):
        """Should update routine metadata successfully."""
        repo = RoutineRepository(mock_chroma_collection)
        routine_id = "routine_123"
        new_metadata = {"category": "technique", "tags": "scales", "state": "completed"}

        repo.update_metadata(routine_id, new_metadata)

        mock_chroma_collection.update.assert_called_once_with(
            ids=[routine_id],
            metadatas=[new_metadata]
        )

    def test_update_metadata_invalid_id(self, mock_chroma_collection):
        """Should raise ValueError when routine_id is invalid."""
        repo = RoutineRepository(mock_chroma_collection)

        with pytest.raises(ValueError, match="Routine ID must be a non-empty string"):
            repo.update_metadata("", {"state": "completed"})

        with pytest.raises(ValueError, match="Routine ID must be a non-empty string"):
            repo.update_metadata(None, {"state": "completed"})

    def test_update_metadata_invalid_metadata(self, mock_chroma_collection):
        """Should raise ValueError when metadata is invalid."""
        repo = RoutineRepository(mock_chroma_collection)

        with pytest.raises(ValueError, match="Metadata must be a non-empty dictionary"):
            repo.update_metadata("routine_123", {})

        with pytest.raises(ValueError, match="Metadata must be a non-empty dictionary"):
            repo.update_metadata("routine_123", None)

    def test_update_metadata_database_error(self, mock_chroma_collection):
        """Should raise RuntimeError when update fails."""
        mock_chroma_collection.update.side_effect = Exception("Database error")
        repo = RoutineRepository(mock_chroma_collection)

        with pytest.raises(RuntimeError, match="Failed to update routine"):
            repo.update_metadata("routine_123", {"state": "completed"})


@pytest.mark.unit
class TestRoutineRepositoryGetById:
    """Tests for get_by_id method."""

    def test_get_by_id_success(self, mock_chroma_collection, sample_chroma_get_result):
        """Should return a single routine by ID."""
        mock_chroma_collection.get.return_value = sample_chroma_get_result
        repo = RoutineRepository(mock_chroma_collection)

        result = repo.get_by_id("routine_123")

        mock_chroma_collection.get.assert_called_once_with(ids=["routine_123"])
        assert result["id"] == "routine_123"
        assert "document" in result
        assert "metadata" in result

    def test_get_by_id_not_found(self, mock_chroma_collection):
        """Should return None when routine is not found."""
        mock_chroma_collection.get.return_value = {"ids": [], "documents": [], "metadatas": []}
        repo = RoutineRepository(mock_chroma_collection)

        result = repo.get_by_id("nonexistent")

        assert result is None

    def test_get_by_id_invalid_id(self, mock_chroma_collection):
        """Should raise ValueError when routine_id is invalid."""
        repo = RoutineRepository(mock_chroma_collection)

        with pytest.raises(ValueError, match="Routine ID must be a non-empty string"):
            repo.get_by_id("")

        with pytest.raises(ValueError, match="Routine ID must be a non-empty string"):
            repo.get_by_id(None)

    def test_get_by_id_database_error(self, mock_chroma_collection):
        """Should raise RuntimeError when query fails."""
        mock_chroma_collection.get.side_effect = Exception("Database error")
        repo = RoutineRepository(mock_chroma_collection)

        with pytest.raises(RuntimeError, match="Failed to fetch routine"):
            repo.get_by_id("routine_123")
