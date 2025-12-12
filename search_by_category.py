import logging
from database import get_collection

logger = logging.getLogger(__name__)


def search_by_category(category, state="not_completed"):
    """
    Search for practice routines by category and optional state.

    Args:
        category (str): The category to search for (e.g., 'daily', 'one_day').
        state (str|None): The state filter ('not_completed', 'completed', or None for all).

    Returns:
        dict: ChromaDB results containing matching routines.

    Raises:
        ValueError: If category is empty or invalid.
        RuntimeError: If database query fails.
    """
    try:
        # Validate inputs
        if not category or not isinstance(category, str):
            logger.error(f"Invalid category parameter: {category}")
            raise ValueError("Category must be a non-empty string")

        logger.info(f"Searching routines: category='{category}', state='{state}'")

        # Get the shared collection instance
        collection = get_collection()

        # Build filter based on whether state is provided
        if state is None:
            # If state is None, only filter by category (get all states)
            where_filter = {"category": category}
        else:
            # Filter by both category and state
            where_filter = {
                "$and": [
                    {"category": category},
                    {"state": state}
                ]
            }

        results = collection.get(where=where_filter)
        logger.info(f"Found {len(results.get('documents', []))} routines")
        return results

    except ValueError:
        raise  # Re-raise ValueError as-is
    except Exception as e:
        logger.error(f"Error searching by category: {e}", exc_info=True)
        raise RuntimeError(f"Database query failed: {e}") from e

if __name__ == "__main__":
    print("This script is intended to be imported as a module.")
