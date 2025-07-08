#!/usr/bin/env python3
"""
Integration tests for httpx-based LLM API calls (OpenAI, Anthropic, gzip).
"""

import os
import pytest
import trainloop_llm_logging as tl
from .harness import IntegrationTestHarness, require_openai_key, require_anthropic_key


class TestHttpxIntegration:
    """Test httpx library integration (sync and async)."""

    @require_openai_key()
    def test_httpx_sync_openai(self):
        """Test sync httpx with OpenAI API."""
        with IntegrationTestHarness("httpx_sync") as harness:
            import httpx

            client = httpx.Client()
            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                    **tl.trainloop_tag("test-httpx-sync"),
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
                entry, expected_model="gpt-4o-mini", expected_tag="test-httpx-sync"
            )

    @require_openai_key()
    @pytest.mark.asyncio
    async def test_httpx_async_openai(self):
        """Test async httpx with OpenAI API."""
        with IntegrationTestHarness("httpx_async") as harness:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                        **tl.trainloop_tag("test-httpx-async"),
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
                entry, expected_model="gpt-4o-mini", expected_tag="test-httpx-async"
            )


class TestAnthropicIntegration:
    """Test with Anthropic API to ensure multi-provider support (httpx)."""

    @require_anthropic_key()
    def test_httpx_anthropic(self):
        """Test httpx with Anthropic API."""
        with IntegrationTestHarness("anthropic") as harness:
            import httpx

            client = httpx.Client()
            headers = {
                "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
                **tl.trainloop_tag("test-anthropic"),
            }
            headers = {k: v for k, v in headers.items() if v is not None}
            response = client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 10,
                    "messages": [
                        {"role": "user", "content": "Say hello in exactly 3 words"}
                    ],
                },
            )
            assert response.status_code == 200
            result = response.json()
            assert "content" in result
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"
            entry = entries[0]
            assert harness.validate_entry(
                entry,
                expected_model="claude-3-haiku-20240307",
                expected_tag="test-anthropic",
            )


class TestGzipResponseHandling:
    """Test that gzipped responses are handled correctly (httpx)."""

    @require_openai_key()
    def test_gzipped_response_with_httpx(self):
        """Test that gzipped responses from OpenAI are properly handled."""
        with IntegrationTestHarness("gzip") as harness:
            import httpx

            client = httpx.Client()
            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                    "Accept-Encoding": "gzip",
                    **tl.trainloop_tag("test-gzip"),
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "user",
                            "content": "Write a short poem about computers (2-3 lines)",
                        }
                    ],
                    "max_tokens": 50,
                },
            )
            assert response.status_code == 200
            result = response.json()
            assert "choices" in result
            print(
                f"Response encoding: {response.headers.get('content-encoding', 'none')}"
            )
            entries = harness.wait_for_entries(expected_count=1, tag="test-gzip")
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"
            entry = entries[0]
            assert harness.validate_entry(
                entry, expected_model="gpt-4o-mini", expected_tag="test-gzip"
            )
            assert (
                len(entry["output"]["content"]) > 10
            ), "Content should be substantial for a poem"
            print(f"✅ Captured content: {entry['output']['content'][:100]}...")
