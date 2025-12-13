"""
Database module for ChromaDB and OpenAI client management.

This module provides singleton access to ChromaDB and OpenAI clients,
ensuring they are initialized only once per Python process.
"""

import logging
import chromadb
from openai import OpenAI, OpenAIError
from src.config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

# Export constants for backward compatibility
DB_PATH = settings.DB_PATH
COLLECTION_NAME = settings.COLLECTION_NAME
EMBEDDING_MODEL = settings.EMBEDDING_MODEL

# Module-level singletons (created once on first import)
_chroma_client = None
_openai_client = None
_collection = None


def get_chroma_client():
    """
    Get or create the ChromaDB client.

    Returns:
        chromadb.PersistentClient: The ChromaDB client instance.

    Raises:
        RuntimeError: If ChromaDB client cannot be initialized.
    """
    global _chroma_client
    if _chroma_client is None:
        try:
            logger.info(f"Initializing ChromaDB client at {DB_PATH}")
            _chroma_client = chromadb.PersistentClient(path=DB_PATH)
            logger.info("ChromaDB client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise RuntimeError(f"Could not initialize ChromaDB at {DB_PATH}: {e}") from e
    return _chroma_client


def get_openai_client():
    """
    Get or create the OpenAI client.

    Returns:
        OpenAI: The OpenAI client instance.

    Raises:
        RuntimeError: If OpenAI client cannot be initialized.
    """
    global _openai_client
    if _openai_client is None:
        try:
            logger.info("Initializing OpenAI client")
            _openai_client = OpenAI()
            logger.info("OpenAI client initialized successfully")
        except OpenAIError as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise RuntimeError(f"Could not initialize OpenAI client: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error initializing OpenAI client: {e}")
            raise RuntimeError(f"Unexpected error with OpenAI client: {e}") from e
    return _openai_client


def get_collection():
    """
    Get or create the guitar_routines collection.

    Returns:
        chromadb.Collection: The guitar_routines collection instance.

    Raises:
        RuntimeError: If collection cannot be created or accessed.
    """
    global _collection
    if _collection is None:
        try:
            client = get_chroma_client()
            logger.info(f"Getting or creating collection: {COLLECTION_NAME}")
            _collection = client.get_or_create_collection(name=COLLECTION_NAME)
            logger.info(f"Collection '{COLLECTION_NAME}' ready")
        except Exception as e:
            logger.error(f"Failed to get/create collection '{COLLECTION_NAME}': {e}")
            raise RuntimeError(f"Could not access collection '{COLLECTION_NAME}': {e}") from e
    return _collection
