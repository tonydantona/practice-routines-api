"""
Database management commands for CLI.
"""

import uuid
import logging
import json
from pathlib import Path
from typing import List
from chromadb import Collection
from openai import OpenAI
from src.config.settings import settings
from src.services.embedding_service import EmbeddingService
from src.models.routine import Routine

logger = logging.getLogger(__name__)


class DatabaseCommands:
    """Handles database build and management operations."""

    def __init__(
        self,
        openai_client: OpenAI,
        collection: Collection,
        embedding_service: EmbeddingService
    ):
        """
        Initialize database commands.

        Args:
            openai_client: OpenAI client instance.
            collection: ChromaDB collection.
            embedding_service: Service for generating embeddings.
        """
        self.openai_client = openai_client
        self.collection = collection
        self.embedding_service = embedding_service

    def build_database(self, force: bool = False):
        """
        Build the ChromaDB database from routines file.

        Args:
            force: If True, delete existing data before rebuilding.

        Raises:
            ValueError: If routines data is invalid.
            RuntimeError: If database operations fail.
        """
        try:
            # Load routines from file
            routines = self._load_routines_from_file(settings.ROUTINES_FILE)
            logger.info(f"Building database with {len(routines)} routines (force={force})")

            # Check if database already has data
            existing = self.collection.get()
            has_data = existing["documents"] and len(existing["documents"]) > 0

            if has_data and not force:
                logger.info("Database already populated, skipping rebuild")
                print("Database already populated. Skipping rebuild. Use force=True to rebuild.")
                return

            # Handle force rebuild
            if force and has_data:
                logger.info("Force rebuild: deleting existing routines")
                print("Force rebuild enabled. Deleting existing routines...")
                existing_ids = self.collection.get()["ids"]
                if existing_ids:
                    self.collection.delete(ids=existing_ids)
                    logger.info(f"Deleted {len(existing_ids)} existing routines")

            # Extract texts and validate
            texts = [r.text for r in routines]
            logger.info(f"Validated {len(texts)} routine texts")

            # Generate embeddings using service
            embeddings = self.embedding_service.generate_embeddings_batch(texts)

            # Prepare metadata
            metadatas = [
                {
                    "category": r.category,
                    "tags": ", ".join(r.tags),
                    "state": r.state
                }
                for r in routines
            ]
            logger.info(f"Prepared metadata for {len(metadatas)} routines")

            # Add to ChromaDB
            ids = [str(uuid.uuid4()) for _ in routines]
            logger.info(f"Adding {len(ids)} routines to collection")
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadatas
            )
            logger.info("Successfully added all routines to database")
            print("Routines added and saved.")

        except ValueError:
            raise
        except RuntimeError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error building database: {e}", exc_info=True)
            raise RuntimeError(f"Database build failed: {e}") from e

    def _load_routines_from_file(self, filepath: str) -> List[Routine]:
        """
        Load routines from a JSON file.

        Args:
            filepath: Path to the routines JSON file.

        Returns:
            List of Routine objects.

        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If file content is invalid.
            RuntimeError: If file loading fails.
        """
        try:
            filepath_obj = Path(filepath)

            if not filepath_obj.exists():
                logger.error(f"Routines file not found: {filepath}")
                raise FileNotFoundError(f"Routines file not found: {filepath}")

            logger.info(f"Loading routines from {filepath}")

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                logger.error(f"Invalid routines file format: expected list, got {type(data)}")
                raise ValueError("Routines file must contain a JSON array")

            # Convert to Routine objects (this validates each routine)
            routines = [Routine.from_dict(item) for item in data]

            logger.info(f"Loaded {len(routines)} routines from {filepath}")
            return routines

        except FileNotFoundError:
            raise
        except ValueError:
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in routines file: {e}")
            raise ValueError(f"Invalid JSON in {filepath}: {e}") from e
        except Exception as e:
            logger.error(f"Error loading routines from {filepath}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to load routines from {filepath}: {e}") from e
