import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_routines_from_file(filepath):
    """
    Load routines from a JSON file.

    Args:
        filepath (str): Path to the JSON file containing routines.

    Returns:
        list: List of routine dictionaries.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file is not valid JSON or has invalid structure.
        RuntimeError: If file cannot be read.
    """
    try:
        filepath_obj = Path(filepath)

        if not filepath_obj.exists():
            logger.error(f"Routines file not found: {filepath}")
            raise FileNotFoundError(f"Routines file not found: {filepath}")

        logger.info(f"Loading routines from {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            routines = json.load(f)

        if not isinstance(routines, list):
            logger.error(f"Invalid routines file format: expected list, got {type(routines)}")
            raise ValueError("Routines file must contain a JSON array")

        logger.info(f"Loaded {len(routines)} routines from {filepath}")
        return routines

    except FileNotFoundError:
        raise  # Re-raise as-is
    except ValueError:
        raise  # Re-raise as-is (for invalid list structure)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in routines file: {e}")
        raise ValueError(f"Invalid JSON in {filepath}: {e}") from e
    except Exception as e:
        logger.error(f"Error loading routines from {filepath}: {e}", exc_info=True)
        raise RuntimeError(f"Failed to load routines from {filepath}: {e}") from e

def display_results(results):
    """
    Display all routines returned in a standard Chroma result format.

    Args:
        results (dict): ChromaDB results with 'ids', 'documents', and 'metadatas' keys.
    """
    try:
        if not results or not isinstance(results, dict):
            logger.warning("Invalid results format for display")
            print("\nNo results to display.\n")
            return

        ids = results.get("ids", [])
        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])

        if not ids:
            print("\nNo practice routines found.\n")
            return

        print("\nPractice routines:\n")
        for doc_id, doc, meta in zip(ids, documents, metadatas):
            print(f"ID      : {doc_id}")
            print(f"Text    : {doc}")
            print(f"Category: {meta.get('category') if meta else 'N/A'}")
            print(f"Tags    : {meta.get('tags') if meta else 'N/A'}")
            print(f"State   : {meta.get('state') if meta else 'N/A'}")
            print("-" * 40)
    except Exception as e:
        logger.error(f"Error displaying results: {e}", exc_info=True)
        print("\nError displaying results.\n")

def display_search_text_results(query, results):
    """
    Display results from a semantic search, including scores.

    Args:
        query (str): The search query.
        results (dict): ChromaDB search results with nested lists.
    """
    try:
        if not results or not isinstance(results, dict):
            logger.warning("Invalid search results format for display")
            print(f"\nNo results for: '{query}'\n")
            return

        print(f"\nTop matches for: '{query}'\n")

        # Handle nested list structure from ChromaDB query results
        ids = results.get("ids", [[]])[0] if results.get("ids") else []
        documents = results.get("documents", [[]])[0] if results.get("documents") else []
        metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
        distances = results.get("distances", [[]])[0] if results.get("distances") else []

        if not documents:
            print("No close matches — try rewording your query.")
            return

        for doc_id, doc, meta, score in zip(ids, documents, metadatas, distances):
            print(f"Score   : {score:.4f}")
            print(f"ID      : {doc_id}")
            print(f"Text    : {doc}")
            print(f"Category: {meta.get('category') if meta else 'N/A'}")
            print(f"Tags    : {meta.get('tags') if meta else 'N/A'}")
            print("-" * 40)
    except Exception as e:
        logger.error(f"Error displaying search results: {e}", exc_info=True)
        print("\nError displaying search results.\n")

if __name__ == "__main__":
    print("This script is intended to be imported as a module.")