import logging
from database import get_collection

logger = logging.getLogger(__name__)


def get_all_practice_routines():
    """
    Get all practice routines from the database.

    Returns:
        dict: ChromaDB results containing all routines.

    Raises:
        RuntimeError: If database query fails.
    """
    try:
        logger.info("Fetching all practice routines")

        # Get the shared collection instance
        collection = get_collection()

        # Get all documents
        results = collection.get()

        logger.info(f"Retrieved {len(results.get('documents', []))} routines")
        return results

    except Exception as e:
        logger.error(f"Error fetching all routines: {e}", exc_info=True)
        raise RuntimeError(f"Failed to fetch routines: {e}") from e

if __name__ == "__main__":
    print("This script is intended to be imported as a module.")