import logging

logger = logging.getLogger(__name__)


def mark_routine_completed(routine_id, collection, completed_state="completed"):
    """
    Marks a routine as completed by updating its 'state' metadata.

    This function efficiently updates only the metadata without regenerating
    embeddings or making unnecessary OpenAI API calls.

    Args:
        routine_id (str): The UUID of the routine to update.
        collection: The Chroma collection where the routine is stored.
        completed_state (str): The state to set (default: "completed").

    Returns:
        bool: True if update was successful, False if routine not found or error occurred.
    """
    try:
        # Validate inputs
        if not routine_id:
            logger.error("mark_routine_completed called with empty routine_id")
            print("Error: Routine ID cannot be empty.")
            return False

        logger.info(f"Attempting to update routine {routine_id} to state '{completed_state}'")

        # Verify the routine exists
        results = collection.get(ids=[routine_id])
        if not results["documents"]:
            logger.warning(f"No routine found with ID: {routine_id}")
            print(f"No routine found with ID: {routine_id}")
            return False

        # Get current metadata and update the state
        meta = results["metadatas"][0]
        meta["state"] = completed_state

        # Update only the metadata - no need to regenerate embeddings!
        collection.update(
            ids=[routine_id],
            metadatas=[meta]
        )

        logger.info(f"Successfully updated routine {routine_id} to state '{completed_state}'")
        print(f"Routine {routine_id} state updated to '{completed_state}'.")
        return True

    except Exception as e:
        logger.error(f"Error updating routine {routine_id}: {e}", exc_info=True)
        print(f"Error updating routine: {e}")
        return False

if __name__ == "__main__":
    print("This script is intended to be imported as a module.")