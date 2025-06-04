"""
Lightweight "LLM Judge" helper for TrainLoop metrics.

╭───────────────────────────────────────────────╮
│  PUBLIC API   (everything most users need)   │
╰───────────────────────────────────────────────╯
    >>> from trainloop.judge import assert_true
    verdict = assert_true(                    # 0 = fail, 1 = pass
        "This is something a dog would do.",           # claim
        "This is not something a dog would do.",       # contrapositive claim
        cfg={
            "models": ["openai/gpt-4o", "anthropic/claude-3-sonnet"],
            "calls_per_model_per_claim": 5,     # k  (per-model, per-claim)
            "temperature": 0.7,
            "template": DEFAULT_TEMPLATE,     # user-editable
        }
    )

    # optional access to prompt wrapper
    print(make_prompt("A claim."))            # prints the final prompt

╭───────────────────────────────────────────────╮
│  DESIGN DECISIONS                             │
╰───────────────────────────────────────────────╯
• Atomic:  each metric calls `assert_true()` for each claim → returns int (0/1).
• Deterministic panel:   models read from config, round-robin order,
  each model asked *exactly* `k` times per claim (self-consistency).
• XOR sanity:  If a single sample answers *both* claims the same,
  discard that sample before voting.
• Confidence:  Comes from the XOR mechanism and ensemble voting,
  not from individual model confidence scores (which are unreliable).

• Panel vote rules
       ┌──────────────────────────────────────┐
       │ claim "yes" wins →      return 1     │
       │ claim "no"  wins →      return 0     │
       │ every model abstains →  return 0 +   │
       │                          WARNING log │
       └──────────────────────────────────────┘

• Config precedence:
    1.  `cfg` arg to `assert_true()` (dict) **overrides**
    2.  `trainloop.config.yaml` → `trainloop:` → `judge:` section → overrides
    3.  hard-coded defaults (`["openai/gpt-4o"]`, `k=3`, `temp=0.7`)

• Prompt template is user-exposed (`DEFAULT_TEMPLATE` or override via cfg)
  so teams can add extra instructions, reasoning format, etc.

"""

from __future__ import annotations
from typing import List, Dict, Tuple, Optional
import json
from pathlib import Path
import asyncio
import re
import logging
from functools import lru_cache
import yaml
import litellm

# Configure logging
logger = logging.getLogger(__name__)

# ─────────── 1. DEFAULTS & USER-FACING TEMPLATE  ──────────── #

DEFAULT_TEMPLATE: str = """
You are a strict evaluator.

Think step-by-step about the claim and provide your reasoning.
Then give a clear verdict of true/false or yes/no that answers the claim.

<claim>
{claim}
</claim>

Your response should be in the following format:
<reasoning>
[Your step-by-step analysis of the claim]
</reasoning>

<result>
[true or false / yes or no]
</result>
"""


def make_prompt(claim: str, template: str = DEFAULT_TEMPLATE) -> str:
    """
    Render the final prompt sent to each LLM sample.

    Users can call this to inspect / customise the prompt.
    """
    return template.format(claim=claim)


# ─────────── 2. CORE JUDGE HELPERS (PRIVATE) ─────────────── #


class _JudgeEngine:
    """
    Not exported.

    Handles:
    • deterministic model scheduling
    • LiteLLM async calls
    • self-consistency (k votes / model / claim)
    • XOR sanity check
    • majority aggregation
    """

    def __init__(self, cfg: Dict):
        self.models = cfg.get("models", ["openai/gpt-4o"])
        self.k = cfg.get("calls_per_model_per_claim", 3)
        self.temperature = cfg.get("temperature", 0.7)
        self.template = cfg.get("template", DEFAULT_TEMPLATE)

        # Ensure models is a list
        if isinstance(self.models, str):
            self.models = [self.models]

    async def _call_llm(self, model: str, prompt: str) -> str:
        """Make a single LLM call and return the response."""
        try:
            response = await litellm.acompletion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.warning(f"LLM call failed for {model}: {e}")
            return ""

    def _extract_verdict(self, response: str) -> Optional[bool]:
        """Extract true/false verdict from LLM response."""
        if not response:
            return None

        # Look for result section
        result_match = re.search(
            r"<result>\s*(.*?)\s*</result>", response, re.IGNORECASE | re.DOTALL
        )
        if result_match:
            result_text = result_match.group(1).lower().strip()
        else:
            # Fallback: look for true/false or yes/no anywhere in the response
            result_text = response.lower()

        # Check for positive indicators
        if any(word in result_text for word in ["true", "yes", "correct", "valid"]):
            return True
        # Check for negative indicators
        elif any(
            word in result_text for word in ["false", "no", "incorrect", "invalid"]
        ):
            return False

        return None

    async def _get_model_votes(
        self, model: str, yes_prompt: str, no_prompt: str
    ) -> Tuple[List[bool], List[bool]]:
        """Get k votes from a single model for both claims."""
        yes_tasks = [self._call_llm(model, yes_prompt) for _ in range(self.k)]
        no_tasks = [self._call_llm(model, no_prompt) for _ in range(self.k)]

        yes_responses = await asyncio.gather(*yes_tasks)
        no_responses = await asyncio.gather(*no_tasks)

        yes_votes = [self._extract_verdict(resp) for resp in yes_responses]
        no_votes = [self._extract_verdict(resp) for resp in no_responses]

        return yes_votes, no_votes

    def _apply_xor_sanity(
        self, yes_votes: List[bool], no_votes: List[bool]
    ) -> Tuple[List[bool], List[bool]]:
        """Apply XOR sanity check: discard samples that answer both claims the same."""
        filtered_yes = []
        filtered_no = []

        for y, n in zip(yes_votes, no_votes):
            if y is None or n is None:
                # Keep samples where at least one is None (abstention)
                filtered_yes.append(y)
                filtered_no.append(n)
            elif y != n:
                # Keep samples where answers differ (expected behavior)
                filtered_yes.append(y)
                filtered_no.append(n)
            else:
                # Discard samples where y == n (both True or both False)
                logger.warning(
                    "Discarding sample where both claims answered the same (unreliable judge)"
                )
                continue

        return filtered_yes, filtered_no

    def yes_no(self, yes_prompt: str, no_prompt: str) -> int:
        """
        Evaluate the two prompts and return pass/fail.

        pass   → 1 if YES wins, 0 if NO wins or tie/abstain
        """
        # Run async evaluation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._async_yes_no(yes_prompt, no_prompt))
        finally:
            loop.close()

    async def _async_yes_no(self, yes_prompt: str, no_prompt: str) -> int:
        """Async implementation of yes_no."""
        all_yes_votes = []
        all_no_votes = []

        # Collect votes from all models
        for model in self.models:
            yes_votes, no_votes = await self._get_model_votes(
                model, yes_prompt, no_prompt
            )

            # Apply XOR sanity check per model
            yes_votes, no_votes = self._apply_xor_sanity(yes_votes, no_votes)

            all_yes_votes.extend(yes_votes)
            all_no_votes.extend(no_votes)

        # Count votes (None values are abstentions)
        yes_count = sum(1 for v in all_yes_votes if v is True)
        no_count = sum(1 for v in all_no_votes if v is True)

        # Check if all models abstained
        total_votes = len([v for v in all_yes_votes + all_no_votes if v is not None])
        if total_votes == 0:
            logger.warning("All models abstained from voting")
            return 0

        # Determine winner
        return 1 if yes_count > no_count else 0


# ─────────── 3. SINGLETON ENGINE LOADER ──────────────────── #


def _find_config_file() -> Optional[Path]:
    """Find trainloop.config.yaml by searching up from current directory."""
    current = Path.cwd()

    while current != current.parent:
        config_path = current / "trainloop.config.yaml"
        if config_path.exists():
            return config_path
        current = current.parent

    return None


def _load_cfg(override: Optional[Dict]) -> Dict:
    """
    Merge hard-coded defaults ← YAML ← override (highest priority).
    Returns the final config dict.
    """
    # Start with defaults
    cfg = {
        "models": ["openai/gpt-4o"],
        "calls_per_model_per_claim": 3,
        "temperature": 0.7,
        "template": DEFAULT_TEMPLATE,
    }

    # Try to load from YAML
    config_path = _find_config_file()
    if config_path:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                yaml_config = yaml.safe_load(f)
                # Look for judge config inside trainloop section
                if (
                    yaml_config
                    and "trainloop" in yaml_config
                    and "judge" in yaml_config["trainloop"]
                ):
                    cfg.update(yaml_config["trainloop"]["judge"])
        except Exception as e:
            logger.warning(f"Failed to load judge config from {config_path}: {e}")

    # Apply overrides
    if override:
        cfg.update(override)

    return cfg


@lru_cache(maxsize=32)
def _engine(cfg_override_str: Optional[str]) -> _JudgeEngine:
    """
    Cache a single _JudgeEngine per (frozen) config so import-time
    overrides don't leak across calls.

    Note: We use a string representation of the config for caching
    since dicts are not hashable.
    """
    # Convert string back to dict (or None)
    cfg_override = None
    if cfg_override_str:
        cfg_override = json.loads(cfg_override_str)

    cfg = _load_cfg(cfg_override)
    return _JudgeEngine(cfg)


# ─────────── 4. PUBLIC API  ───────────────────────────────── #


def assert_true(
    yes_claim: str,
    no_claim: str,
    cfg: Optional[Dict] = None,
) -> int:
    """
    Main API: evaluate a binary claim using LLM panel.

    Returns:
        1 if `yes_claim` wins the panel vote
        0 if `no_claim` wins or tie/abstain

    Example:
        verdict = assert_true(
            "This is something a dog would do.",
            "This is not something a dog would do."
        )
    """
    # Convert cfg to string for caching (None becomes None)
    cfg_str = None
    if cfg is not None:
        cfg_str = json.dumps(cfg, sort_keys=True)

    engine = _engine(cfg_str)
    yes_prompt = make_prompt(yes_claim, engine.template)
    no_prompt = make_prompt(no_claim, engine.template)
    return engine.yes_no(yes_prompt, no_prompt)
