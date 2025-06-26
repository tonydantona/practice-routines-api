import chromadb

def get_all_practice_routines():
  # Load the persistent DB
  client = chromadb.PersistentClient(path="chroma_data")
  collection = client.get_or_create_collection(name="guitar_routines")

  # Get all documents
  results = collection.get()

  return results

if __name__ == "__main__":
    print("This script is intended to be imported as a module.")