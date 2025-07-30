"""
shoebill_ai package for interacting with LLM models.

This package provides a high-level API for interacting with LLM models.
Users should import from this package, not from the application, domain, or infrastructure layers directly.
"""

__all__ = [
    # Main service classes
    'EmbeddingService',
    'TextService',
    'MultimodalService',
    'VisionService',

    # Agent orchestration
    'AgentOrchestrator',
]

# Import main service classes
from .application import EmbeddingService, TextService, MultimodalService, VisionService

# Import agent orchestration
from .application.workflows.agent_orchestrator import AgentOrchestrator
