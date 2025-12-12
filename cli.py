"""
Command-line interface for the Practice Routines API.

This module provides an interactive menu for managing guitar practice routines,
including database building, searching, and updating routine states.
"""

from database import get_collection, get_openai_client
from build_chroma_db import build_db
from search_by_category import search_by_category
from search_by_text import search_routines
from get_all_routines import get_all_practice_routines
from mark_routine_completed import mark_routine_completed
from get_not_completed_routines import get_not_completed_routines
from utils import load_routines_from_file, display_results, display_search_text_results
from config import settings


def menu():
    """Interactive CLI menu for managing practice routines."""
    # Initialize database connections and load routines
    openai_client = get_openai_client()
    collection = get_collection()
    routines = load_routines_from_file(settings.ROUTINES_FILE)

    # Default search parameters
    top_n = 5
    min_score = 1.0

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


if __name__ == "__main__":
    menu()