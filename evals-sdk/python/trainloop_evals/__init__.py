"""
TrainLoop Evals SDK
-------------------
Public surface:

    • HEADER_NAME
    • trainloop_tag(tag) → {"X-Trainloop-Tag": tag}
    • collect()          → bootstrap + auto-patch

Import this once, early in your program:

    import trainloop_evals as tl
    tl.collect()

Everything else happens automatically.
"""

from .register import HEADER_NAME, trainloop_tag, collect

__all__ = ["HEADER_NAME", "trainloop_tag", "collect"]
