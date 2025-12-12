"""
Database module for ChromaDB and OpenAI client management.

This module provides singleton access to ChromaDB and OpenAI clients,
ensuring they are initialized only once per Python process.
"""

import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables once
load_dotenv()

# Validate API key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OpenAI API key not found. Make sure it's in your .env file.")

# Configuration constants
DB_PATH = "../data/chroma_data"
COLLECTION_NAME = "guitar_routines"
EMBEDDING_MODEL = "text-embedding-3-small"

# Module-level singletons (created once on first import)
_chroma_client = None
_openai_client = None
_collection = None


def get_chroma_client():
    """
    Get or create the ChromaDB client.

    Returns:
        chromadb.PersistentClient: The ChromaDB client instance.
    """
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=DB_PATH)
    return _chroma_client


def get_openai_client():
    """
    Get or create the OpenAI client.

    Returns:
        OpenAI: The OpenAI client instance.
    """
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI()
    return _openai_client


def get_collection():
    """
    Get or create the guitar_routines collection.

    Returns:
        chromadb.Collection: The guitar_routines collection instance.
    """
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return _collection
