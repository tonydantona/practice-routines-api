import chromadb
import os
from openai import OpenAI

def get_not_completed_routines(collection):
    """
    Lists all routines where 'state' is not 'completed'.
    """
    results = collection.get(where={"state": "not_completed"})

    return results

if __name__ == "__main__":
    print("This script is intended to be imported as a module.")