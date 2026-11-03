"""SLIF Research Intelligence & Cross-Verification Package."""

from skillforge.research.cross_verifier import (
    CrossSourceVerifier,
    ResearchCache,
    classify_source_tier,
    extract_atomic_claims,
)

__all__ = [
    "CrossSourceVerifier",
    "ResearchCache",
    "classify_source_tier",
    "extract_atomic_claims",
]

