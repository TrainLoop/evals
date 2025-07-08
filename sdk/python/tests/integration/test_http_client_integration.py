#!/usr/bin/env python3
"""
Integration tests for http.client-based LLM API calls (OpenAI).
"""

import os
import json
import trainloop_llm_logging as tl
from .harness import IntegrationTestHarness, require_openai_key


class TestHttpClientIntegration:
    """Test http.client library integration."""

    @require_openai_key()
    def test_http_client_openai(self):
        """Test http.client with OpenAI API."""
        with IntegrationTestHarness("http_client") as harness:
            import http.client

            payload = json.dumps(
                {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "user", "content": "Say hello in exactly 3 words"}
                    ],
                    "max_tokens": 10,
                }
            )
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json",
                "Content-Length": str(len(payload)),
                **tl.trainloop_tag("test-http-client"),
            }
            conn = http.client.HTTPSConnection("api.openai.com")
            conn.request("POST", "/v1/chat/completions", payload, headers)
            response = conn.getresponse()
            assert response.status == 200
            data = response.read().decode()
            result = json.loads(data)
            assert "choices" in result
            conn.close()
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"
            entry = entries[0]
            assert harness.validate_entry(
                entry, expected_model="gpt-4o-mini", expected_tag="test-http-client"
            )
