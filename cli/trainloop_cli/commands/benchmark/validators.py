"""Validation functions for benchmark command."""

from __future__ import annotations

import os
from typing import List

from .constants import (
    BAD,
    EMOJI_WARNING,
    INFO_COLOR,
    RESET_COLOR,
    PROVIDER_KEY_MAP,
)


def validate_provider_keys(providers: List[str]) -> List[str]:
    """Validate that API keys exist for each provider."""
    valid_providers = []
    missing_keys = []

    for provider in providers:
        # Extract provider name from model string (e.g., "openai/gpt-4" -> "openai")
        provider_prefix = provider.split("/")[0].lower()

        if provider_prefix in PROVIDER_KEY_MAP:
            env_var = PROVIDER_KEY_MAP[provider_prefix]
            if os.environ.get(env_var):
                valid_providers.append(provider)
            else:
                missing_keys.append(f"{provider} (missing {env_var})")
        else:
            # For unknown providers, assume they're valid and let LiteLLM handle it
            valid_providers.append(provider)

    if missing_keys:
        print(f"\n{EMOJI_WARNING} Missing API keys for providers:")
        for missing in missing_keys:
            print(f"  {BAD} {missing}")
        print(
            f"\n{INFO_COLOR}Please set the required environment variables or update your .env file.{RESET_COLOR}"
        )

    return valid_providers