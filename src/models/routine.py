"""
Data models for practice routines.
"""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Routine:
    """Represents a guitar practice routine."""

    text: str
    category: str
    tags: List[str]
    state: str = "not_completed"

    def __post_init__(self):
        """Validate routine data after initialization."""
        if not self.text:
            raise ValueError("Routine text cannot be empty")
        if not self.category:
            raise ValueError("Routine category cannot be empty")
        if self.state not in ["not_completed", "completed"]:
            raise ValueError(f"Invalid state: {self.state}")

    @classmethod
    def from_dict(cls, data: dict) -> 'Routine':
        """Create a Routine from a dictionary."""
        return cls(
            text=data.get("text", ""),
            category=data.get("category", ""),
            tags=data.get("tags", []),
            state=data.get("state", "not_completed")
        )

    def to_dict(self) -> dict:
        """Convert routine to dictionary."""
        return {
            "text": self.text,
            "category": self.category,
            "tags": self.tags,
            "state": self.state
        }


@dataclass
class RoutineSearchResult:
    """Represents a search result with metadata."""

    id: str
    text: str
    category: str
    tags: str  # Comma-separated string from ChromaDB
    state: str
    score: Optional[float] = None  # For semantic search results

    @classmethod
    def from_chroma_result(cls, doc_id: str, document: str, metadata: dict, score: Optional[float] = None) -> 'RoutineSearchResult':
        """Create from ChromaDB query result."""
        return cls(
            id=doc_id,
            text=document,
            category=metadata.get("category", ""),
            tags=metadata.get("tags", ""),
            state=metadata.get("state", "not_completed"),
            score=score
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        result = {
            "id": self.id,
            "text": self.text,
            "category": self.category,
            "tags": self.tags,
            "state": self.state
        }
        if self.score is not None:
            result["score"] = self.score
        return result
