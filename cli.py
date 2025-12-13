"""
Command-line interface for the Practice Routines API.

This module provides an interactive menu for managing guitar practice routines,
including database building, searching, and updating routine states.
"""

import logging
import sys
from database import get_collection, get_openai_client
from build_chroma_db import build_db
from search_by_category import search_by_category
from search_by_text import search_routines
from get_all_routines import get_all_practice_routines
from mark_routine_completed import mark_routine_completed
from get_not_completed_routines import get_not_completed_routines
from utils import load_routines_from_file, display_results, display_search_text_results
from config import settings

# Configure logging for CLI
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def menu():
    """Interactive CLI menu for managing practice routines."""
    try:
        # Initialize database connections and load routines
        logger.info("Initializing CLI application")

        try:
            openai_client = get_openai_client()
            collection = get_collection()
            logger.info("Database connections initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database connections: {e}")
            print(f"Error: Could not connect to databases. {e}")
            sys.exit(1)

        try:
            routines = load_routines_from_file(settings.ROUTINES_FILE)
            logger.info(f"Loaded {len(routines)} routines from {settings.ROUTINES_FILE}")
        except Exception as e:
            logger.error(f"Failed to load routines file: {e}")
            print(f"Error: Could not load routines file. {e}")
            sys.exit(1)

        # Default search parameters
        top_n = 5
        min_score = 1.0

        while True:
            try:
                print("\n--- Virtual Jar Menu ---")
                print("0. Build database")
                print("1. Get all practice routines")
                print("2. Search routines by category")
                print("3. Search routines by text")
                print("4. Get not-completed routines")
                print("5. Mark a routine as completed")
                print("6. Exit")

                choice = input("Enter choice (0-6): ").strip()

                if choice == "0":
                    try:
                        # Ask user if they want to force rebuild
                        confirm = input("Database already exists. Rebuild from scratch? (y/N): ").strip().lower()
                        force_rebuild = confirm == "y"
                        print("Building database...")
                        build_db(openai_client, collection, routines, force=force_rebuild)
                    except Exception as e:
                        logger.error(f"Error building database: {e}")
                        print(f"Error building database: {e}")

                elif choice == "1":
                    try:
                        results = get_all_practice_routines()
                        display_results(results)
                    except Exception as e:
                        logger.error(f"Error getting all routines: {e}")
                        print(f"Error retrieving routines: {e}")

                elif choice == "2":
                    try:
                        category = input("Enter category (e.g., daily, one_day): ").strip()
                        if not category:
                            print("Error: Category cannot be empty.")
                            continue
                        results = search_by_category(category)
                        display_results(results)
                    except Exception as e:
                        logger.error(f"Error searching by category: {e}")
                        print(f"Error searching by category: {e}")

                elif choice == "3":
                    try:
                        query = input("Enter search phrase (e.g., scales): ").strip()
                        if not query:
                            print("Error: Search query cannot be empty.")
                            continue
                        text_search_results = search_routines(query, collection, openai_client, top_n, min_score)
                        display_search_text_results(query, text_search_results)
                    except Exception as e:
                        logger.error(f"Error searching by text: {e}")
                        print(f"Error searching by text: {e}")

                elif choice == "4":
                    try:
                        results = get_not_completed_routines(collection)
                        display_results(results)
                    except Exception as e:
                        logger.error(f"Error getting not-completed routines: {e}")
                        print(f"Error retrieving not-completed routines: {e}")

                elif choice == "5":
                    try:
                        routine_id = input("Enter ID of routine to mark as completed: ").strip()
                        if not routine_id:
                            print("Error: Routine ID cannot be empty.")
                            continue
                        mark_routine_completed(routine_id, collection)
                        print("Routine marked as completed.")
                    except Exception as e:
                        logger.error(f"Error marking routine completed: {e}")
                        print(f"Error marking routine as completed: {e}")

                elif choice == "6":
                    logger.info("User exiting CLI")
                    print("Goodbye!")
                    break

                else:
                    print("Invalid choice. Try again.")

            except KeyboardInterrupt:
                logger.info("User interrupted with Ctrl+C")
                print("\n\nInterrupted. Goodbye!")
                break
            except EOFError:
                logger.info("User ended input (EOF)")
                print("\n\nGoodbye!")
                break

    except Exception as e:
        logger.error(f"Unexpected error in CLI: {e}", exc_info=True)
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    menu()