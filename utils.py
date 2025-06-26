import json

def load_routines_from_file(filepath):
    """
    Loads routines from a JSON file.
    """
    with open(filepath, "r") as f:
        return json.load(f)

def display_results(results):
    """
    Display all routines returned in a standard Chroma result format.
    """
    print("\nPractice routines:\n")
    for doc_id, doc, meta in zip(results["ids"], results["documents"], results["metadatas"]):
        print(f"ID      : {doc_id}")
        print(f"Text    : {doc}")
        print(f"Category: {meta.get('category')}")
        print(f"Tags    : {meta.get('tags')}")
        print(f"State   : {meta.get('state')}")
        print("-" * 40)

def display_search_text_results(query, results):
    """
    Display results from a semantic search, including scores.
    """
    print(f"\nTop matches for: '{query}'\n")

    if not results["documents"][0]:
        print("No close matches — try rewording your query.")
        return

    for doc_id, doc, meta, score in zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        print(f"Score   : {score:.4f}")
        print(f"ID      : {doc_id}")
        print(f"Text    : {doc}")
        print(f"Category: {meta.get('category')}")
        print(f"Tags    : {meta.get('tags')}")
        print("-" * 40)

if __name__ == "__main__":
    print("This script is intended to be imported as a module.")