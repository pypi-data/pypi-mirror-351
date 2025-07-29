"""
EnrichMCP: A framework for exposing structured data to AI agents.

This library provides a clean, declarative API for defining data models
as entities with relationships between them, making it easier for AI
assistants to interact with structured data.
"""

__version__ = "0.1.0"

# Public exports
from .app import EnrichMCP
from .context import EnrichContext
from .entity import EnrichModel
from .relationship import (
    Relationship,
)

__all__ = [
    "EnrichContext",
    "EnrichMCP",
    "EnrichModel",
    "Relationship",
]
