"""Global configuration settings.

This module defines the global configuration settings that apply across the application,
including chunking, embedding, and logging configurations.
"""

from pydantic import Field

from qdrant_loader.config.base import BaseConfig
from qdrant_loader.config.chunking import ChunkingConfig
from qdrant_loader.config.embedding import EmbeddingConfig
from qdrant_loader.config.sources import SourcesConfig
from qdrant_loader.config.state import StateManagementConfig
from qdrant_loader.config.types import GlobalConfigDict


class SemanticAnalysisConfig(BaseConfig):
    """Configuration for semantic analysis."""

    num_topics: int = Field(
        default=3, description="Number of topics to extract using LDA"
    )

    lda_passes: int = Field(default=10, description="Number of passes for LDA training")


class GlobalConfig(BaseConfig):
    """Global configuration settings."""

    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    semantic_analysis: SemanticAnalysisConfig = Field(
        default_factory=SemanticAnalysisConfig,
        description="Semantic analysis configuration",
    )
    state_management: StateManagementConfig = Field(
        default_factory=lambda: StateManagementConfig(database_path=":memory:"),
        description="State management configuration",
    )
    sources: SourcesConfig = Field(default_factory=SourcesConfig)

    def __init__(self, **data):
        """Initialize global configuration."""
        # If skip_validation is True, use in-memory database for state management
        skip_validation = data.pop("skip_validation", False)
        if skip_validation:
            data["state_management"] = {
                "database_path": ":memory:",
                "table_prefix": "qdrant_loader_",
                "connection_pool": {"size": 5, "timeout": 30},
            }
        super().__init__(**data)

    def to_dict(self) -> GlobalConfigDict:
        """Convert the configuration to a dictionary."""
        return {
            "chunking": {
                "chunk_size": self.chunking.chunk_size,
                "chunk_overlap": self.chunking.chunk_overlap,
            },
            "embedding": self.embedding.model_dump(),
            "semantic_analysis": {
                "num_topics": self.semantic_analysis.num_topics,
                "lda_passes": self.semantic_analysis.lda_passes,
            },
            "sources": self.sources.to_dict(),
            "state_management": self.state_management.to_dict(),
        }
