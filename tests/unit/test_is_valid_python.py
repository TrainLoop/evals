"""Unit tests for the is_valid_python metric in the TrainLoop registry."""

import pytest
from registry.types import Sample
from registry.metrics.is_valid_python import is_valid_python, _extract_python_code
from registry.metrics.is_valid_python.config import config as metric_config
import registry.metrics_registry as metrics_registry


def _create_sample(content: str) -> Sample:
    """Helper to create a test sample with given output content."""
    return Sample(
        duration_ms=120,
        tag="code-eval",
        input=[{"role": "user", "content": "Write a python function"}],
        output={"content": content},
        model="qwen-2.5-coder-32b",
        model_params={"temperature": 0.2},
        start_time_ms=1000,
        end_time_ms=1120,
        url="https://api.openai.com/v1/chat/completions",
        location={"tag": "code-eval", "lineNumber": "10"},
    )


class TestExtractPythonCode:
    """Tests for _extract_python_code helper."""

    def test_extract_markdown_python_block(self):
        content = "Here is your function:\n```python\ndef greet(name: str) -> str:\n    return f'Hello, {name}!'\n```\nEnjoy!"
        extracted = _extract_python_code(content)
        assert "def greet(name: str) -> str:" in extracted
        assert "Here is your function" not in extracted

    def test_extract_markdown_py_block(self):
        content = "```py\nx = 10\ny = 20\nprint(x + y)\n```"
        extracted = _extract_python_code(content)
        assert extracted == "x = 10\ny = 20\nprint(x + y)"

    def test_extract_generic_code_block(self):
        content = "```\nimport math\nval = math.sqrt(16)\n```"
        extracted = _extract_python_code(content)
        assert "import math" in extracted

    def test_extract_raw_python_code(self):
        content = "def square(n):\n    return n * n"
        extracted = _extract_python_code(content)
        assert extracted == content

    def test_extract_empty_or_none(self):
        assert _extract_python_code("") == ""
        assert _extract_python_code(None) == ""


class TestIsValidPythonMetric:
    """Tests for is_valid_python metric evaluator."""

    def test_valid_raw_code_passes(self):
        sample = _create_sample("def add(a, b):\n    return a + b\n")
        assert is_valid_python(sample) == 1

    def test_valid_markdown_code_passes(self):
        code = "```python\nclass Model:\n    def __init__(self):\n        self.val = 42\n```"
        sample = _create_sample(code)
        assert is_valid_python(sample) == 1

    def test_syntax_error_fails(self):
        sample = _create_sample("def broken_func(a, :\n    return a")
        assert is_valid_python(sample) == 0

    def test_indentation_error_fails(self):
        sample = _create_sample("def bad_indent():\nx = 1\nreturn x")
        assert is_valid_python(sample) == 0

    def test_unmatched_parentheses_fails(self):
        sample = _create_sample("print('missing close parenthesis'")
        assert is_valid_python(sample) == 0

    def test_empty_content_fails(self):
        sample = _create_sample("")
        assert is_valid_python(sample) == 0

    def test_whitespace_only_fails(self):
        sample = _create_sample("   \n\n   ")
        assert is_valid_python(sample) == 0

    def test_invalid_sample_structure_handled_gracefully(self):
        assert is_valid_python(None) == 0
        
        # Missing output dict
        invalid_sample = Sample(
            duration_ms=0, tag="", input=[], output=None, model="",
            model_params={}, start_time_ms=0, end_time_ms=0, url="", location={}
        )
        assert is_valid_python(invalid_sample) == 0

    def test_metric_metadata_config(self):
        assert metric_config.name == "is_valid_python"
        assert metric_config.author == "TrainLoop Team"
        assert "python" in metric_config.tags
        assert "syntax" in metric_config.tags
        assert "ast" in metric_config.tags

    def test_exported_in_metrics_registry(self):
        assert "is_valid_python" in metrics_registry.__all__
        assert hasattr(metrics_registry, "is_valid_python")
        assert callable(metrics_registry.is_valid_python)
