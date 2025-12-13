"""
Service for generating and managing embeddings.
"""

import logging
from typing import List
from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using OpenAI."""

    def __init__(self, openai_client: OpenAI, model: str = "text-embedding-3-small"):
        """
        Initialize the embedding service.

        Args:
            openai_client: OpenAI API client.
            model: Embedding model to use.
        """
        self.client = openai_client
        self.model = model

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for a single text.

        Args:
            text: Text to embed.

        Returns:
            List of floats representing the embedding vector.

        Raises:
            ValueError: If text is invalid.
            RuntimeError: If OpenAI API call fails.
        """
        if not text or not isinstance(text, str):
            logger.error(f"Invalid text parameter: {text}")
            raise ValueError("Text must be a non-empty string")

        try:
            logger.debug(f"Generating embedding for text: '{text[:50]}...'")
            response = self.client.embeddings.create(
                input=[text],
                model=self.model
            )
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding (dimension: {len(embedding)})")
            return embedding

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"Failed to generate embedding: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error generating embedding: {e}")
            raise RuntimeError(f"Embedding generation failed: {e}") from e

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in a batch.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embedding vectors.

        Raises:
            ValueError: If texts is invalid.
            RuntimeError: If OpenAI API call fails.
        """
        if not texts or not isinstance(texts, list):
            logger.error(f"Invalid texts parameter: {type(texts)}")
            raise ValueError("Texts must be a non-empty list")

        if not all(isinstance(t, str) and t for t in texts):
            logger.error("All texts must be non-empty strings")
            raise ValueError("All texts must be non-empty strings")

        try:
            logger.info(f"Generating embeddings for {len(texts)} texts using {self.model}")
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"Failed to generate embeddings: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error generating embeddings: {e}")
            raise RuntimeError(f"Batch embedding generation failed: {e}") from e
