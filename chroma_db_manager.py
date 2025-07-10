import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

from build_chroma_db import build_db
from search_by_category import search_by_category
from search_by_text import search_routines
from get_all_routines import get_all_practice_routines
from mark_routine_completed import mark_routine_completed
from get_not_completed_routines import get_not_completed_routines

from utils import load_routines_from_file, display_results, display_search_text_results

# This line loads the variables from your .env file
load_dotenv()

# This line gets the API key from the environment variables
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

if not os.environ["OPENAI_API_KEY"]:
    raise ValueError("OpenAI API key not found. Make sure it's in your .env file.")


# Initialize OpenAI clien
openai_client = OpenAI()

# Set up ChromaDB 
client = chromadb.PersistentClient(path="chroma_data")

 # my practice routines
routines = load_routines_from_file("routines/routines.json")

collection = client.get_or_create_collection(name="guitar_routines")

# build_db(openai_client, collection, routines)
# results = search_by_category("daily")


# Example search
query = "pentatonic"
top_n=5
min_score=1.0
# text_search_results = search_routines(query, collection, openai_client, top_n, min_score)

def menu():
    while True:
        print("\n--- Virtual Jar Menu ---")
        print("0. Build database")
        print("1. Get all practice routines")
        print("2. Search routines by category")
        print("3. Search routines by text")
        print("4. Get not-completed routines")
        print("5. Mark a routine as completed")
        print("6. Exit")

        choice = input("Enter choice (0-6): ").strip()

        if choice == "0":
            # Ask user if they want to force rebuild
            confirm = input("Database already exists. Rebuild from scratch? (y/N): ").strip().lower()
            force_rebuild = confirm == "y"
            print("Building database...")
            build_db(openai_client, collection, routines, force=force_rebuild)
           
        elif choice == "1":
            results = get_all_practice_routines()
            display_results(results)

        elif choice == "2":
            category = input("Enter category (e.g., daily, one_day): ").strip()
            results = search_by_category(category)
            display_results(results)

        elif choice == "3":
            query = input("Enter search phrase (e.g., scales): ").strip()
            text_search_results = search_routines(query, collection, openai_client, top_n, min_score)
            display_search_text_results(query, text_search_results)

        elif choice == "4":
            results = get_not_completed_routines(collection)
            display_results(results)

        elif choice == "5":
            routine_id = input("Enter ID of routine to mark as completed: ").strip()
            mark_routine_completed(routine_id, collection)

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Try again.")


# def display_results(results):
#     print("\nMatching routines:\n")
#     for doc_id, doc, meta in zip(results["ids"], results["documents"], results["metadatas"]):
#         print(f"ID      : {doc_id}")
#         print(f"Text    : {doc}")
#         print(f"Category: {meta.get('category')}")
#         print(f"Tags    : {meta.get('tags')}")
#         print(f"State   : {meta.get('state')}")
#         print("-" * 40)

# def display_search_text_results(query, results):
#     print(f"\nTop matches for: '{query}'\n")

#     if not results["documents"][0]:
#         print("No close matches — try rewording your query.")
#         return

#     for doc_id, doc, meta, score in zip(
#         results["ids"][0],
#         results["documents"][0],
#         results["metadatas"][0],
#         results["distances"][0]
#     ):
#         print(f"Score   : {score:.4f}")
#         print(f"ID      : {doc_id}")
#         print(f"Text    : {doc}")
#         print(f"Category: {meta.get('category')}")
#         print(f"Tags    : {meta.get('tags')}")
#         print("-" * 40)

# Run the menu
if __name__ == "__main__":
    menu()