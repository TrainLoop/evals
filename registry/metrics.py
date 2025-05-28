"""Registry metrics module - imports all available metrics."""

from .always_pass.always_pass import always_pass

# Export all metrics
__all__ = [
    "always_pass",
]