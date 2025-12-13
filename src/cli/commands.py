"""
CLI commands for managing practice routines.
"""

import logging
import sys
from src.config.settings import settings
from src.config.database import get_chroma_client, get_openai_client, get_collection
from src.repositories.routine_repository import RoutineRepository
from src.services.embedding_service import EmbeddingService
from src.services.routine_service import RoutineService
from src.cli.database_commands import DatabaseCommands
from src.cli.display import Display

# Configure logging for CLI
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CLI:
    """Command-line interface for practice routines."""

    def __init__(self):
        """Initialize the CLI with all dependencies."""
        try:
            logger.info("Initializing CLI application")

            # Initialize database connections
            openai_client = get_openai_client()
            collection = get_collection()
            logger.info("Database connections initialized")

            # Initialize layers
            self.repository = RoutineRepository(collection)
            self.embedding_service = EmbeddingService(openai_client, settings.EMBEDDING_MODEL)
            self.routine_service = RoutineService(self.repository, self.embedding_service)

            # Initialize command handlers
            self.db_commands = DatabaseCommands(
                openai_client,
                collection,
                self.embedding_service
            )
            self.display = Display()

        except Exception as e:
            logger.error(f"Failed to initialize CLI: {e}")
            print(f"Error: Could not initialize CLI. {e}")
            sys.exit(1)

    def run(self):
        """Run the interactive CLI menu."""
        try:
            # Default search parameters
            top_n = 5
            min_score = 1.0

            while True:
                try:
                    self._print_menu()
                    choice = input("Enter choice (0-6): ").strip()

                    if choice == "0":
                        self._handle_build_database()
                    elif choice == "1":
                        self._handle_get_all_routines()
                    elif choice == "2":
                        self._handle_search_by_category()
                    elif choice == "3":
                        self._handle_search_by_text(top_n, min_score)
                    elif choice == "4":
                        self._handle_get_not_completed()
                    elif choice == "5":
                        self._handle_mark_completed()
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

    def _print_menu(self):
        """Print the CLI menu."""
        print("\n--- Virtual Jar Menu ---")
        print("0. Build database")
        print("1. Get all practice routines")
        print("2. Search routines by category")
        print("3. Search routines by text")
        print("4. Get not-completed routines")
        print("5. Mark a routine as completed")
        print("6. Exit")

    def _handle_build_database(self):
        """Handle database build command."""
        try:
            confirm = input("Database already exists. Rebuild from scratch? (y/N): ").strip().lower()
            force_rebuild = confirm == "y"
            print("Building database...")
            self.db_commands.build_database(force=force_rebuild)
        except Exception as e:
            logger.error(f"Error building database: {e}")
            print(f"Error building database: {e}")

    def _handle_get_all_routines(self):
        """Handle get all routines command."""
        try:
            routines = self.routine_service.get_all_routines()
            self.display.show_routines(routines)
        except Exception as e:
            logger.error(f"Error getting all routines: {e}")
            print(f"Error retrieving routines: {e}")

    def _handle_search_by_category(self):
        """Handle search by category command."""
        try:
            category = input("Enter category (e.g., daily, one_day): ").strip()
            if not category:
                print("Error: Category cannot be empty.")
                return

            routines = self.routine_service.get_routines_by_category(category)
            self.display.show_routines(routines)
        except Exception as e:
            logger.error(f"Error searching by category: {e}")
            print(f"Error searching by category: {e}")

    def _handle_search_by_text(self, top_n: int, min_score: float):
        """Handle semantic search command."""
        try:
            query = input("Enter search phrase (e.g., scales): ").strip()
            if not query:
                print("Error: Search query cannot be empty.")
                return

            routines = self.routine_service.search_routines(query, top_n, min_score)
            self.display.show_search_results(query, routines)
        except Exception as e:
            logger.error(f"Error searching by text: {e}")
            print(f"Error searching by text: {e}")

    def _handle_get_not_completed(self):
        """Handle get not-completed routines command."""
        try:
            routines = self.routine_service.get_not_completed_routines()
            self.display.show_routines(routines)
        except Exception as e:
            logger.error(f"Error getting not-completed routines: {e}")
            print(f"Error retrieving not-completed routines: {e}")

    def _handle_mark_completed(self):
        """Handle mark routine completed command."""
        try:
            routine_id = input("Enter ID of routine to mark as completed: ").strip()
            if not routine_id:
                print("Error: Routine ID cannot be empty.")
                return

            self.routine_service.mark_routine_completed(routine_id)
            print("Routine marked as completed.")
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            logger.error(f"Error marking routine completed: {e}")
            print(f"Error marking routine as completed: {e}")


def main():
    """CLI entry point."""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
