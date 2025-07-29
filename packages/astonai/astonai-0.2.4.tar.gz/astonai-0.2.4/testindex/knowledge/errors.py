#!/usr/bin/env python3
"""
Custom error classes for the knowledge system.
"""


class TestIntelligenceError(Exception):
    """Base class for all errors in the knowledge system."""
    pass


# Graph Database Errors
class Neo4jConnectionError(TestIntelligenceError):
    """Raised when there's an error connecting to the Neo4j database."""
    pass


class Neo4jQueryError(TestIntelligenceError):
    """Raised when there's an error executing a Neo4j query."""
    pass


class BatchOperationError(TestIntelligenceError):
    """Raised when there's an error in a batch database operation."""
    pass


# Static Analysis Errors
class StaticAnalysisError(TestIntelligenceError):
    """Raised when there's an error in static code analysis."""
    pass


# Schema Errors
class SchemaVersionMismatchError(TestIntelligenceError):
    """Raised when the database schema version doesn't match the expected version."""
    pass


# Vector Store Errors
class VectorStoreError(TestIntelligenceError):
    """Base class for vector store related errors."""
    pass


class VectorOperationError(VectorStoreError):
    """Raised when an operation on vectors fails."""
    pass


class VectorInvalidDimensionError(VectorStoreError):
    """Raised when vector dimensions don't match expected dimensions."""
    pass


# Embedding Errors
class EmbeddingError(TestIntelligenceError):
    """Base class for embedding related errors."""
    pass


class EmbeddingGenerationError(EmbeddingError):
    """Raised when there's an error generating embeddings."""
    pass


class EmbeddingModelError(EmbeddingError):
    """Raised when there's an issue with the embedding model."""
    pass


class EmbeddingRateLimitError(EmbeddingError):
    """Raised when API rate limits are exceeded."""
    pass


class EmbeddingTokenLimitError(EmbeddingError):
    """Raised when content exceeds token limits."""
    pass 