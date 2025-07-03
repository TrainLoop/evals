"""
TrainLoop LLM Logging SDK
-------------------
Public surface:

    • HEADER_NAME
    • trainloop_tag(tag) → {"X-Trainloop-Tag": tag}
    • collect()          → bootstrap + auto-patch

Import this once, early in your program:

    import trainloop_llm_logging as tl
    tl.collect()

Everything else happens automatically.
"""

from .register import HEADER_NAME, trainloop_tag, collect, flush

__all__ = ["HEADER_NAME", "trainloop_tag", "collect", "flush"]
