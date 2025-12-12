import uuid
from database import EMBEDDING_MODEL

def build_db(openai_client, collection, routines, force=False):

  existing = collection.get()
  if existing["documents"] and not force:
      print("Database already populated. Skipping rebuild. Use force=True to rebuild.")
      return
  
  if force:
      print("Force rebuild enabled. Deleting existing routines...")
      existing_ids = collection.get()["ids"]
      if existing_ids:
          collection.delete(ids=existing_ids)
  
  # this function generates embeddings using OpenAI and adds them to Chroma
  def embed(texts):
      response = openai_client.embeddings.create(
          input=texts,
          model=EMBEDDING_MODEL
      )
      return [item.embedding for item in response.data]

  # we extract the text from each routine (that's what we want to embed and what Chroma expects)
  texts = [r["text"] for r in routines]

  # generate embeddings
  embeddings = embed(texts)

  collection.add(
    documents=texts,
    embeddings=embeddings,
    ids = [str(uuid.uuid4()) for _ in routines],
    metadatas = [
      {
          "category": r["category"],
          "tags": ", ".join(r.get("tags", [])),  # Turn tag list into a string
          "state": r.get("state", "not_completed")  # Default to 'not_completed' if not specified
      }
      for r in routines
    ]
  )

  print("Routines added and saved.")