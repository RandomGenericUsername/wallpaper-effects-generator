"""Layered effects configuration system.

Public API:
    configure() - Configure the effects system
    load_effects() - Load and merge effects from all layers
"""

__version__ = "0.1.0"


def configure(project_root=None):
    """Configure the effects system (placeholder)."""
    raise NotImplementedError("To be implemented")


def load_effects():
    """Load effects configuration (placeholder)."""
    raise NotImplementedError("To be implemented")


__all__ = [
    "__version__",
    "configure",
    "load_effects",
]
