import logging

logger = logging.getLogger(__name__)


def get_not_completed_routines(collection):
    """
    Get all practice routines that are not completed.

    Args:
        collection: The Chroma collection to query.

    Returns:
        dict: ChromaDB results containing not-completed routines.

    Raises:
        RuntimeError: If database query fails.
    """
    try:
        logger.info("Fetching not-completed routines")

        results = collection.get(where={"state": "not_completed"})

        logger.info(f"Found {len(results.get('documents', []))} not-completed routines")
        return results

    except Exception as e:
        logger.error(f"Error fetching not-completed routines: {e}", exc_info=True)
        raise RuntimeError(f"Failed to fetch not-completed routines: {e}") from e

if __name__ == "__main__":
    print("This script is intended to be imported as a module.")