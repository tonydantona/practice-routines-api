import chromadb

def search_by_category(category, state="not_completed"):
  # Load the persistent DB
  client = chromadb.PersistentClient(path="chroma_data")
  collection = client.get_or_create_collection(name="guitar_routines")

  # filter by category and state
  results = collection.get(
      where={
          "$and": [
              {"category": category},
              {"state": state}
          ]
      }
  )
  return results

if __name__ == "__main__":
    print("This script is intended to be imported as a module.")
