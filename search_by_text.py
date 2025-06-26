import os
import chromadb
from openai import OpenAI

# •	For semantic searches using natural language (like "scales" or "improvise over chords")
# •	Uses OpenAI embeddings and Chroma similarity
# •	Optional: filters weak matches using score threshold (min_score)
# •	Doesn’t use metadata filtering like category or tags

def search_routines(query, collection, openai_client, top_n=5, min_score=0.3):
    """
    Search routines using a semantic query.
    
    Args:
        query (str): The search text (e.g., "scales", "jamming").
        collection: Chroma collection to query.
        openai_client: OpenAI API client.
        top_n (int): Max results to return.
        min_score (float): Max distance allowed (lower is more similar).
    """
    response = openai_client.embeddings.create(
        input=[query],
        model="text-embedding-3-small"
    )
    query_embedding = response.data[0].embedding

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_n
    )

    # Filter results based on min_score
    filtered = [
        (doc_id, doc, meta, score)
        for doc_id, doc, meta, score in zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )
        if score <= min_score
    ]

    if not filtered:
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    ids, docs, metas, scores = zip(*filtered)
    return {
        "ids": [list(ids)],
        "documents": [list(docs)],
        "metadatas": [list(metas)],
        "distances": [list(scores)]
    }

if __name__ == "__main__":
    print("This script is intended to be imported as a module.")