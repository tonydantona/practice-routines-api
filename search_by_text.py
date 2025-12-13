import logging
from openai import OpenAIError
from database import get_collection, get_openai_client, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

# •	For semantic searches using natural language (like "scales" or "improvise over chords")
# •	Uses OpenAI embeddings and Chroma similarity
# •	Optional: filters weak matches using score threshold (min_score)
# •	Doesn't use metadata filtering like category or tags


def search_routines(query, collection=None, openai_client=None, top_n=5, min_score=0.3):
    """
    Search routines using a semantic query.

    Args:
        query (str): The search text (e.g., "scales", "jamming").
        collection: Chroma collection to query (defaults to shared instance).
        openai_client: OpenAI API client (defaults to shared instance).
        top_n (int): Max results to return.
        min_score (float): Max distance allowed (lower is more similar).

    Returns:
        dict: ChromaDB results containing matching routines.

    Raises:
        ValueError: If query is empty or invalid.
        RuntimeError: If OpenAI API call or database query fails.
    """
    try:
        # Validate inputs
        if not query or not isinstance(query, str):
            logger.error(f"Invalid query parameter: {query}")
            raise ValueError("Query must be a non-empty string")

        if top_n < 1:
            logger.error(f"Invalid top_n parameter: {top_n}")
            raise ValueError("top_n must be at least 1")

        logger.info(f"Semantic search for: '{query}' (top_n={top_n}, min_score={min_score})")

        # Use shared instances if not provided
        if collection is None:
            collection = get_collection()
        if openai_client is None:
            openai_client = get_openai_client()

        # Generate embedding using OpenAI
        try:
            response = openai_client.embeddings.create(
                input=[query],
                model=EMBEDDING_MODEL
            )
            query_embedding = response.data[0].embedding
            logger.info(f"Generated embedding for query (dimension: {len(query_embedding)})")
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"Failed to generate embedding: {e}") from e

        # Query the database
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
            logger.info(f"No results met min_score threshold of {min_score}")
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

        ids, docs, metas, scores = zip(*filtered)
        logger.info(f"Found {len(filtered)} results meeting score threshold")

        return {
            "ids": [list(ids)],
            "documents": [list(docs)],
            "metadatas": [list(metas)],
            "distances": [list(scores)]
        }

    except ValueError:
        raise  # Re-raise ValueError as-is
    except RuntimeError:
        raise  # Re-raise RuntimeError as-is
    except Exception as e:
        logger.error(f"Error in semantic search: {e}", exc_info=True)
        raise RuntimeError(f"Semantic search failed: {e}") from e

if __name__ == "__main__":
    print("This script is intended to be imported as a module.")