#!/usr/bin/env python3
"""
Integration tests for requests-based LLM API calls (OpenAI).
"""

import os
import trainloop_llm_logging as tl
from .harness import IntegrationTestHarness, require_openai_key


class TestRequestsIntegration:
    """Test requests library integration."""

    @require_openai_key()
    def test_requests_openai(self):
        """Test requests library with OpenAI API."""
        with IntegrationTestHarness("requests") as harness:
            import requests

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                timeout=10,
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                    "Content-Type": "application/json",
                    **tl.trainloop_tag("test-requests"),
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "user", "content": "Say hello in exactly 3 words"}
                    ],
                    "max_tokens": 10,
                },
            )
            assert response.status_code == 200
            result = response.json()
            assert "choices" in result
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"
            entry = entries[0]
            assert harness.validate_entry(
                entry, expected_model="gpt-4o-mini", expected_tag="test-requests"
            )
