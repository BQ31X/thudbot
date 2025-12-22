"""
TEF Configuration Management

Centralized configuration with CLI override support.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


# Calculate project root from this file's location
# config.py is at tools/tef/config.py, so parents[2] gives us project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Sanity check: verify we're actually at project root
if not (PROJECT_ROOT / "apps").exists() or not (PROJECT_ROOT / "tools").exists():
    raise RuntimeError(
        f"PROJECT_ROOT calculation incorrect. Expected project root but got: {PROJECT_ROOT}\n"
        f"This likely means config.py was moved or parents[N] index is wrong."
    )


@dataclass
class TEFConfig:
    """
    Configuration for Thudbot Evaluation Framework.
    
    Default paths are relative to PROJECT_ROOT for consistency regardless of cwd.
    Embedding settings must match the collection being evaluated.
    """
    # Qdrant connection
    qdrant_url: str = "http://localhost:6333"
    collection_name: str = "Thudbot_Hints"
    benchmark_path: str = str(PROJECT_ROOT / "tools/tef/benchmark/benchmark_tef.csv")
    
    # Embedding configuration
    # CRITICAL: Must match the collection's embedding configuration
    embedding_provider: str = "openai"  # "openai" or "local"
    embedding_model: Optional[str] = None  # Override default (if None, uses provider default)
    
    # Retrieval parameters
    k_values: List[int] = field(default_factory=lambda: [1, 3, 5, 10])
    
    # Output
    output_dir: str = str(PROJECT_ROOT / "tools/tef/results")
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.embedding_provider not in ["openai", "local"]:
            raise ValueError(
                f"Invalid embedding_provider: {self.embedding_provider}. "
                f"Must be 'openai' or 'local'"
            )
        
        if not self.k_values:
            raise ValueError("k_values cannot be empty")
        
        if any(k <= 0 for k in self.k_values):
            raise ValueError("All k_values must be positive integers")

