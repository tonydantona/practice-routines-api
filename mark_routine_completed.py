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
        bool: True if update was successful, False if routine not found.
    """
    # Verify the routine exists
    results = collection.get(ids=[routine_id])
    if not results["documents"]:
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

    print(f"Routine {routine_id} state updated to '{completed_state}'.")
    return True

if __name__ == "__main__":
    print("This script is intended to be imported as a module.")