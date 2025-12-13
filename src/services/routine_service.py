"""
Business logic for practice routines.
"""

import logging
import random
from typing import List, Optional, Dict, Any
from src.repositories.routine_repository import RoutineRepository
from src.services.embedding_service import EmbeddingService
from src.models.routine import RoutineSearchResult

logger = logging.getLogger(__name__)


class RoutineService:
    """Service layer for routine business logic."""

    def __init__(self, repository: RoutineRepository, embedding_service: EmbeddingService):
        """
        Initialize the routine service.

        Args:
            repository: Repository for data access.
            embedding_service: Service for generating embeddings.
        """
        self.repository = repository
        self.embedding_service = embedding_service

    def get_all_routines(self) -> List[RoutineSearchResult]:
        """
        Get all practice routines.

        Returns:
            List of RoutineSearchResult objects.

        Raises:
            RuntimeError: If database query fails.
        """
        logger.info("Getting all routines")
        results = self.repository.get_all()

        return [
            RoutineSearchResult.from_chroma_result(doc_id, doc, meta)
            for doc_id, doc, meta in zip(
                results["ids"],
                results["documents"],
                results["metadatas"]
            )
        ]

    def get_routines_by_category(
        self,
        category: str,
        state: Optional[str] = None
    ) -> List[RoutineSearchResult]:
        """
        Get routines filtered by category and optionally by state.

        Args:
            category: Category to filter by.
            state: Optional state filter.

        Returns:
            List of RoutineSearchResult objects.

        Raises:
            ValueError: If parameters are invalid.
            RuntimeError: If database query fails.
        """
        logger.info(f"Getting routines: category={category}, state={state}")
        results = self.repository.get_by_category(category, state)

        return [
            RoutineSearchResult.from_chroma_result(doc_id, doc, meta)
            for doc_id, doc, meta in zip(
                results["ids"],
                results["documents"],
                results["metadatas"]
            )
        ]

    def get_random_routine_by_category(
        self,
        category: str,
        state: Optional[str] = None
    ) -> Optional[RoutineSearchResult]:
        """
        Get a random routine from a category.

        Args:
            category: Category to filter by.
            state: Optional state filter.

        Returns:
            A random RoutineSearchResult or None if no routines found.

        Raises:
            ValueError: If parameters are invalid.
            RuntimeError: If database query fails.
        """
        routines = self.get_routines_by_category(category, state)

        if not routines:
            logger.info(f"No routines found for category={category}, state={state}")
            return None

        random_routine = random.choice(routines)
        logger.info(f"Selected random routine from {len(routines)} options")
        return random_routine

    def get_not_completed_routines(self) -> List[RoutineSearchResult]:
        """
        Get all routines that are not completed.

        Returns:
            List of RoutineSearchResult objects.

        Raises:
            RuntimeError: If database query fails.
        """
        logger.info("Getting not-completed routines")
        results = self.repository.get_by_state("not_completed")

        return [
            RoutineSearchResult.from_chroma_result(doc_id, doc, meta)
            for doc_id, doc, meta in zip(
                results["ids"],
                results["documents"],
                results["metadatas"]
            )
        ]

    def search_routines(
        self,
        query: str,
        top_n: int = 5,
        min_score: float = 0.3
    ) -> List[RoutineSearchResult]:
        """
        Perform semantic search for routines.

        Args:
            query: Search query text.
            top_n: Number of results to return.
            min_score: Minimum similarity score (0-1, lower is better for distance).

        Returns:
            List of RoutineSearchResult objects with scores.

        Raises:
            ValueError: If parameters are invalid.
            RuntimeError: If search fails.
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")

        if top_n < 1:
            raise ValueError("top_n must be at least 1")

        logger.info(f"Semantic search: query='{query}', top_n={top_n}, min_score={min_score}")

        # Generate embedding for query
        embedding = self.embedding_service.generate_embedding(query)

        # Search in database
        results = self.repository.search_by_embedding(embedding, top_n)

        # Handle nested list structure from ChromaDB
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        # Filter by min_score and convert to RoutineSearchResult
        search_results = []
        for doc_id, doc, meta, score in zip(ids, documents, metadatas, distances):
            if score <= min_score:
                search_results.append(
                    RoutineSearchResult.from_chroma_result(doc_id, doc, meta, score)
                )

        logger.info(f"Found {len(search_results)} results after filtering by score")
        return search_results

    def mark_routine_completed(self, routine_id: str) -> None:
        """
        Mark a routine as completed.

        Args:
            routine_id: ID of the routine to mark.

        Raises:
            ValueError: If routine_id is invalid or routine not found.
            RuntimeError: If update fails.
        """
        logger.info(f"Marking routine {routine_id} as completed")

        # Get current routine
        routine = self.repository.get_by_id(routine_id)

        if not routine:
            raise ValueError(f"Routine {routine_id} not found")

        # Update state
        metadata = routine["metadata"]
        metadata["state"] = "completed"

        self.repository.update_metadata(routine_id, metadata)
        logger.info(f"Routine {routine_id} marked as completed")

    def mark_routine_not_completed(self, routine_id: str) -> None:
        """
        Mark a routine as not completed.

        Args:
            routine_id: ID of the routine to mark.

        Raises:
            ValueError: If routine_id is invalid or routine not found.
            RuntimeError: If update fails.
        """
        logger.info(f"Marking routine {routine_id} as not completed")

        # Get current routine
        routine = self.repository.get_by_id(routine_id)

        if not routine:
            raise ValueError(f"Routine {routine_id} not found")

        # Update state
        metadata = routine["metadata"]
        metadata["state"] = "not_completed"

        self.repository.update_metadata(routine_id, metadata)
        logger.info(f"Routine {routine_id} marked as not completed")
