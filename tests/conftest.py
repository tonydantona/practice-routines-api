"""
Shared pytest fixtures for all tests.

This file contains common fixtures that can be used across all test modules.
"""

import pytest
from unittest.mock import Mock
from typing import Dict, Any, List


@pytest.fixture
def sample_routine_metadata() -> Dict[str, Any]:
    """Sample routine metadata for testing."""
    return {
        "category": "technique",
        "tags": "scales,major",
        "state": "not_completed"
    }


@pytest.fixture
def sample_routine_document() -> str:
    """Sample routine document text."""
    return "Practice C major scale in all positions"


@pytest.fixture
def sample_routine_id() -> str:
    """Sample routine ID."""
    return "routine_123"


@pytest.fixture
def sample_chroma_get_result(sample_routine_id, sample_routine_document, sample_routine_metadata) -> Dict[str, Any]:
    """
    Sample ChromaDB get() result with single routine.

    This mimics the structure returned by collection.get()
    """
    return {
        "ids": [sample_routine_id],
        "documents": [sample_routine_document],
        "metadatas": [sample_routine_metadata]
    }


@pytest.fixture
def sample_chroma_get_result_multiple() -> Dict[str, Any]:
    """Sample ChromaDB get() result with multiple routines."""
    return {
        "ids": ["routine_1", "routine_2", "routine_3"],
        "documents": [
            "Practice C major scale",
            "Practice alternate picking",
            "Practice chord changes"
        ],
        "metadatas": [
            {"category": "technique", "tags": "scales", "state": "not_completed"},
            {"category": "technique", "tags": "picking", "state": "completed"},
            {"category": "chords", "tags": "progressions", "state": "not_completed"}
        ]
    }


@pytest.fixture
def sample_chroma_query_result() -> Dict[str, Any]:
    """
    Sample ChromaDB query() result with nested lists.

    Note: query() returns nested lists, unlike get() which returns flat lists.
    """
    return {
        "ids": [["routine_1", "routine_2"]],
        "documents": [["Practice C major scale", "Practice alternate picking"]],
        "metadatas": [[
            {"category": "technique", "tags": "scales", "state": "not_completed"},
            {"category": "technique", "tags": "picking", "state": "completed"}
        ]],
        "distances": [[0.1, 0.2]]
    }


@pytest.fixture
def sample_embedding() -> List[float]:
    """Sample embedding vector."""
    return [0.1, 0.2, 0.3, 0.4, 0.5]


@pytest.fixture
def mock_chroma_collection():
    """Mock ChromaDB collection with common methods."""
    mock = Mock()
    mock.get.return_value = {
        "ids": [],
        "documents": [],
        "metadatas": []
    }
    mock.query.return_value = {
        "ids": [[]],
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]]
    }
    mock.update.return_value = None
    return mock


@pytest.fixture
def mock_embedding_service():
    """Mock embedding service."""
    mock = Mock()
    mock.generate_embedding.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
    return mock


@pytest.fixture
def mock_routine_repository():
    """Mock routine repository with common methods."""
    mock = Mock()
    mock.get_all.return_value = {
        "ids": [],
        "documents": [],
        "metadatas": []
    }
    mock.get_by_category.return_value = {
        "ids": [],
        "documents": [],
        "metadatas": []
    }
    mock.get_by_state.return_value = {
        "ids": [],
        "documents": [],
        "metadatas": []
    }
    mock.search_by_embedding.return_value = {
        "ids": [[]],
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]]
    }
    mock.get_by_id.return_value = None
    mock.update_metadata.return_value = None
    return mock
