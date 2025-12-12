from database import get_collection

def get_all_practice_routines():
  # Get the shared collection instance
  collection = get_collection()

  # Get all documents
  results = collection.get()

  return results

if __name__ == "__main__":
    print("This script is intended to be imported as a module.")