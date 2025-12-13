import uuid
import logging
from openai import OpenAIError
from database import EMBEDDING_MODEL

logger = logging.getLogger(__name__)


def build_db(openai_client, collection, routines, force=False):
    """
    Build the ChromaDB database by generating embeddings and adding routines.

    Args:
        openai_client: OpenAI API client for generating embeddings.
        collection: ChromaDB collection to populate.
        routines (list): List of routine dictionaries to add.
        force (bool): If True, delete existing data before rebuilding.

    Raises:
        ValueError: If routines data is invalid.
        RuntimeError: If database operations or OpenAI API calls fail.
    """
    try:
        # Validate inputs
        if not routines or not isinstance(routines, list):
            logger.error(f"Invalid routines parameter: {type(routines)}")
            raise ValueError("Routines must be a non-empty list")

        logger.info(f"Building database with {len(routines)} routines (force={force})")

        # Check if database already has data
        try:
            existing = collection.get()
            has_data = existing["documents"] and len(existing["documents"]) > 0
        except Exception as e:
            logger.error(f"Error checking existing data: {e}")
            raise RuntimeError(f"Failed to check existing database data: {e}") from e

        if has_data and not force:
            logger.info("Database already populated, skipping rebuild")
            print("Database already populated. Skipping rebuild. Use force=True to rebuild.")
            return

        # Handle force rebuild
        if force and has_data:
            try:
                logger.info("Force rebuild: deleting existing routines")
                print("Force rebuild enabled. Deleting existing routines...")
                existing_ids = collection.get()["ids"]
                if existing_ids:
                    collection.delete(ids=existing_ids)
                    logger.info(f"Deleted {len(existing_ids)} existing routines")
            except Exception as e:
                logger.error(f"Error deleting existing data: {e}")
                raise RuntimeError(f"Failed to delete existing data: {e}") from e

        # Validate routine structure and extract texts
        try:
            texts = []
            for i, routine in enumerate(routines):
                if not isinstance(routine, dict):
                    raise ValueError(f"Routine {i} is not a dictionary: {type(routine)}")
                if "text" not in routine:
                    raise ValueError(f"Routine {i} missing required 'text' field")
                if "category" not in routine:
                    raise ValueError(f"Routine {i} missing required 'category' field")
                texts.append(routine["text"])
            logger.info(f"Validated {len(texts)} routine texts")
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error extracting routine texts: {e}")
            raise ValueError(f"Invalid routine structure: {e}") from e

        # Generate embeddings using OpenAI
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts using {EMBEDDING_MODEL}")
            response = openai_client.embeddings.create(
                input=texts,
                model=EMBEDDING_MODEL
            )
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings")
        except OpenAIError as e:
            logger.error(f"OpenAI API error generating embeddings: {e}")
            raise RuntimeError(f"Failed to generate embeddings: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error generating embeddings: {e}")
            raise RuntimeError(f"Embedding generation failed: {e}") from e

        # Prepare metadata
        try:
            metadatas = [
                {
                    "category": r["category"],
                    "tags": ", ".join(r.get("tags", [])),
                    "state": r.get("state", "not_completed")
                }
                for r in routines
            ]
            logger.info(f"Prepared metadata for {len(metadatas)} routines")
        except Exception as e:
            logger.error(f"Error preparing metadata: {e}")
            raise ValueError(f"Failed to prepare routine metadata: {e}") from e

        # Add to ChromaDB
        try:
            ids = [str(uuid.uuid4()) for _ in routines]
            logger.info(f"Adding {len(ids)} routines to collection")
            collection.add(
                documents=texts,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadatas
            )
            logger.info("Successfully added all routines to database")
            print("Routines added and saved.")
        except Exception as e:
            logger.error(f"Error adding routines to database: {e}")
            raise RuntimeError(f"Failed to add routines to database: {e}") from e

    except ValueError:
        raise
    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error building database: {e}", exc_info=True)
        raise RuntimeError(f"Database build failed: {e}") from e


if __name__ == "__main__":
    print("This script is intended to be imported as a module.")