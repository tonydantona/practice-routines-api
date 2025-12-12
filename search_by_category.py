from database import get_collection

def search_by_category(category, state="not_completed"):
  # Get the shared collection instance
  collection = get_collection()

  # Build filter based on whether state is provided
  if state is None:
      # If state is None, only filter by category (get all states)
      where_filter = {"category": category}
  else:
      # Filter by both category and state
      where_filter = {
          "$and": [
              {"category": category},
              {"state": state}
          ]
      }

  results = collection.get(where=where_filter)
  return results

if __name__ == "__main__":
    print("This script is intended to be imported as a module.")
