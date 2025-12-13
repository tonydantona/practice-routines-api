"""
Repository layer for routine data access.

Handles all ChromaDB interactions.
"""

import logging
from typing import List, Optional, Dict, Any
from chromadb import Collection

logger = logging.getLogger(__name__)


class RoutineRepository:
    """Repository for accessing routine data from ChromaDB."""

    def __init__(self, collection: Collection):
        """
        Initialize the repository.

        Args:
            collection: ChromaDB collection instance.
        """
        self.collection = collection

    def get_all(self) -> Dict[str, Any]:
        """
        Get all routines from the database.

        Returns:
            Dict with 'ids', 'documents', and 'metadatas' keys.

        Raises:
            RuntimeError: If database query fails.
        """
        try:
            logger.info("Fetching all routines")
            results = self.collection.get()
            logger.info(f"Retrieved {len(results.get('ids', []))} routines")
            return results
        except Exception as e:
            logger.error(f"Error fetching all routines: {e}", exc_info=True)
            raise RuntimeError(f"Failed to fetch routines: {e}") from e

    def get_by_category(self, category: str, state: Optional[str] = None) -> Dict[str, Any]:
        """
        Get routines filtered by category and optionally by state.

        Args:
            category: Category to filter by.
            state: Optional state to filter by ('completed', 'not_completed', or None for all).

        Returns:
            Dict with 'ids', 'documents', and 'metadatas' keys.

        Raises:
            ValueError: If category is invalid.
            RuntimeError: If database query fails.
        """
        if not category or not isinstance(category, str):
            logger.error(f"Invalid category parameter: {category}")
            raise ValueError("Category must be a non-empty string")

        try:
            # Build where clause - ChromaDB requires $and for multiple conditions
            if state:
                where = {"$and": [{"category": category}, {"state": state}]}
                logger.info(f"Searching routines: category='{category}', state='{state}'")
            else:
                where = {"category": category}
                logger.info(f"Searching routines: category='{category}' (all states)")

            results = self.collection.get(where=where)
            logger.info(f"Found {len(results.get('ids', []))} routines")
            return results

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error searching by category: {e}", exc_info=True)
            raise RuntimeError(f"Database query failed: {e}") from e

    def get_by_state(self, state: str) -> Dict[str, Any]:
        """
        Get routines filtered by state.

        Args:
            state: State to filter by ('completed' or 'not_completed').

        Returns:
            Dict with 'ids', 'documents', and 'metadatas' keys.

        Raises:
            ValueError: If state is invalid.
            RuntimeError: If database query fails.
        """
        if not state or not isinstance(state, str):
            logger.error(f"Invalid state parameter: {state}")
            raise ValueError("State must be a non-empty string")

        try:
            logger.info(f"Fetching routines with state='{state}'")
            results = self.collection.get(where={"state": state})
            logger.info(f"Found {len(results.get('ids', []))} routines")
            return results
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error fetching by state: {e}", exc_info=True)
            raise RuntimeError(f"Database query failed: {e}") from e

    def search_by_embedding(
        self,
        query_embedding: List[float],
        top_n: int = 5,
        where: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Perform semantic search using embeddings.

        Args:
            query_embedding: The embedding vector to search with.
            top_n: Number of results to return.
            where: Optional metadata filters.

        Returns:
            Dict with nested lists: 'ids', 'documents', 'metadatas', 'distances'.

        Raises:
            ValueError: If parameters are invalid.
            RuntimeError: If database query fails.
        """
        if not query_embedding:
            raise ValueError("Query embedding cannot be empty")
        if top_n < 1:
            raise ValueError("top_n must be at least 1")

        try:
            logger.info(f"Semantic search: top_n={top_n}, filters={where}")
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_n,
                where=where
            )
            logger.info(f"Found {len(results.get('ids', [[]])[0])} results")
            return results
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error in semantic search: {e}", exc_info=True)
            raise RuntimeError(f"Semantic search failed: {e}") from e

    def update_metadata(self, routine_id: str, metadata: Dict[str, Any]) -> None:
        """
        Update metadata for a routine.

        Args:
            routine_id: ID of the routine to update.
            metadata: New metadata dictionary.

        Raises:
            ValueError: If routine_id is invalid.
            RuntimeError: If update fails.
        """
        if not routine_id or not isinstance(routine_id, str):
            logger.error(f"Invalid routine_id: {routine_id}")
            raise ValueError("Routine ID must be a non-empty string")

        if not metadata or not isinstance(metadata, dict):
            logger.error(f"Invalid metadata: {metadata}")
            raise ValueError("Metadata must be a non-empty dictionary")

        try:
            logger.info(f"Updating routine {routine_id}")
            self.collection.update(ids=[routine_id], metadatas=[metadata])
            logger.info(f"Updated routine {routine_id}")
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating routine {routine_id}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to update routine: {e}") from e

    def get_by_id(self, routine_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single routine by ID.

        Args:
            routine_id: ID of the routine.

        Returns:
            Dict with routine data or None if not found.

        Raises:
            ValueError: If routine_id is invalid.
            RuntimeError: If query fails.
        """
        if not routine_id or not isinstance(routine_id, str):
            logger.error(f"Invalid routine_id: {routine_id}")
            raise ValueError("Routine ID must be a non-empty string")

        try:
            logger.info(f"Fetching routine {routine_id}")
            results = self.collection.get(ids=[routine_id])

            if not results["ids"]:
                logger.warning(f"Routine {routine_id} not found")
                return None

            return {
                "id": results["ids"][0],
                "document": results["documents"][0],
                "metadata": results["metadatas"][0]
            }
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error fetching routine {routine_id}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to fetch routine: {e}") from e
