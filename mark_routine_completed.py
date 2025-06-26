import chromadb
import os
from openai import OpenAI

def mark_routine_completed(routine_id, collection, completed_state="completed"):
    """
    Marks a routine as completed by updating its 'state' metadata.
    
    Args:
        routine_id (str): The UUID of the routine to update.
        collection: The Chroma collection where the routine is stored.
    """
    # Step 1: Get the current document
    results = collection.get(ids=[routine_id])
    if not results["documents"]:
        print(f"No routine found with ID: {routine_id}")
        return

    doc = results["documents"][0]
    meta = results["metadatas"][0]

    # Step 2: Delete the old entry
    collection.delete(ids=[routine_id])

    # Step 3: Add it back with updated metadata
    meta["state"] = completed_state

    from openai import OpenAI
    openai_client = OpenAI()
    response = openai_client.embeddings.create(
        input=[doc],
        model="text-embedding-3-small"
    )
    new_embedding = response.data[0].embedding

    collection.add(
        documents=[doc],
        embeddings=[new_embedding],
        ids=[routine_id],
        metadatas=[meta]
    )

    print(f"Routine {routine_id} marked as completed.")

if __name__ == "__main__":
    print("This script is intended to be imported as a module.")