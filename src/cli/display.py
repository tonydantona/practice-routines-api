"""
Display utilities for CLI output.
"""

import logging
from typing import List
from src.models.routine import RoutineSearchResult

logger = logging.getLogger(__name__)


class Display:
    """Handles formatted output for CLI."""

    def show_routines(self, routines: List[RoutineSearchResult]):
        """
        Display a list of routines.

        Args:
            routines: List of RoutineSearchResult objects.
        """
        try:
            if not routines:
                print("\nNo practice routines found.\n")
                return

            print(f"\nPractice routines ({len(routines)} found):\n")

            for routine in routines:
                print(f"ID      : {routine.id}")
                print(f"Text    : {routine.text}")
                print(f"Category: {routine.category}")
                print(f"Tags    : {routine.tags}")
                print(f"State   : {routine.state}")
                print("-" * 40)

        except Exception as e:
            logger.error(f"Error displaying routines: {e}", exc_info=True)
            print("\nError displaying routines.\n")

    def show_search_results(self, query: str, routines: List[RoutineSearchResult]):
        """
        Display semantic search results with scores.

        Args:
            query: The search query.
            routines: List of RoutineSearchResult objects with scores.
        """
        try:
            print(f"\nTop matches for: '{query}'\n")

            if not routines:
                print("No close matches — try rewording your query.")
                return

            for routine in routines:
                if routine.score is not None:
                    print(f"Score   : {routine.score:.4f}")
                print(f"ID      : {routine.id}")
                print(f"Text    : {routine.text}")
                print(f"Category: {routine.category}")
                print(f"Tags    : {routine.tags}")
                print("-" * 40)

        except Exception as e:
            logger.error(f"Error displaying search results: {e}", exc_info=True)
            print("\nError displaying search results.\n")
