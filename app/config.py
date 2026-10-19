"""Configuration management for PatchForge-Nemotron."""

import os
from typing import Optional
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings with environment variable support."""

    # Nebius Token Factory Configuration
    nebius_api_base: str = Field(
        default_factory=lambda: os.getenv("NEBIUS_API_BASE", "https://api.tokenfactory.nebius.com/v1")
    )
    nebius_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("NEBIUS_API_KEY")
    )

    # NVIDIA Models on Nebius Token Factory
    # Nemotron 3 Ultra for deep multi-hop reasoning & unified diff generation
    # Nemotron Nano for fast triage, log ingestion, and syntax validation
    nebius_model_reasoning: str = Field(
        default_factory=lambda: os.getenv("NEBIUS_MODEL_REASONING", "nvidia/nemotron-3-ultra")
    )
    nebius_model_fast: str = Field(
        default_factory=lambda: os.getenv("NEBIUS_MODEL_FAST", "nvidia/nemotron-nano")
    )

    # Tavily Search API Configuration (Bonus category)
    tavily_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("TAVILY_API_KEY")
    )
    tavily_api_base: str = Field(
        default_factory=lambda: os.getenv("TAVILY_API_BASE", "https://api.tavily.com")
    )

    # Server settings
    server_host: str = Field(
        default_factory=lambda: os.getenv("SERVER_HOST", "0.0.0.0")
    )
    server_port: int = Field(
        default_factory=lambda: int(os.getenv("SERVER_PORT", "8000"))
    )

    # Force mock mode override (useful for offline tests and evaluation)
    force_mock: bool = Field(
        default_factory=lambda: os.getenv("FORCE_MOCK", "false").lower() in ("true", "1", "yes")
    )

    @property
    def is_nebius_live(self) -> bool:
        """Return True if a valid Nebius API key is configured and mock is not forced."""
        return bool(
            self.nebius_api_key
            and not self.force_mock
            and self.nebius_api_key.strip() != "your_nebius_token_factory_key"
        )

    @property
    def is_tavily_live(self) -> bool:
        """Return True if a valid Tavily API key is configured and mock is not forced."""
        return bool(
            self.tavily_api_key
            and not self.force_mock
            and self.tavily_api_key.strip() != "your_tavily_api_key"
        )


settings = Settings()
