"""
Metric for deterministic validation of Python code syntax using the Abstract Syntax Tree (AST).

This metric verifies whether model completions contain syntactically valid Python code,
safely parsing code blocks or raw outputs without executing untrusted code.
"""

from __future__ import annotations
import ast
import re
from registry.types import Sample


def _extract_python_code(content: str) -> str:
    """
    Extracts Python code from model output.

    Supports:
    - Markdown fenced code blocks: ```python ... ``` or ```py ... ```
    - Generic fenced code blocks: ``` ... ```
    - Raw Python code text
    """
    if not content or not isinstance(content, str):
        return ""

    # Priority 1: Match explicit ```python or ```py code blocks
    python_block = re.search(r"```(?:python|py)\s*\n(.*?)```", content, re.DOTALL | re.IGNORECASE)
    if python_block:
        return python_block.group(1).strip()

    # Priority 2: Match generic ``` code block
    generic_block = re.search(r"```\s*\n(.*?)```", content, re.DOTALL)
    if generic_block:
        return generic_block.group(1).strip()

    # Fallback: Treat the entire stripped content as raw Python code
    return content.strip()


def is_valid_python(sample: Sample) -> int:
    """
    Evaluates if the model's generated response contains valid Python syntax.

    Args:
        sample: A Sample containing the output response dictionary.

    Returns:
        1 if the extracted code parses into a valid Python AST, 0 otherwise.
    """
    if not sample or not hasattr(sample, "output") or not isinstance(sample.output, dict):
        return 0

    content = sample.output.get("content", "")
    code = _extract_python_code(content)

    if not code:
        return 0

    try:
        ast.parse(code)
        return 1
    except SyntaxError:
        return 0
    except Exception:
        return 0
