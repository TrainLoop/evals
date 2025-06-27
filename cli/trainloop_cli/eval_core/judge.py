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
from typing import Dict, List, Optional, Tuple, Union, Any, TypedDict, cast
import os
import uuid
import datetime
import json
from pathlib import Path
import asyncio
import re
import logging
from functools import lru_cache
from dotenv import load_dotenv, find_dotenv
import yaml
import litellm
import fsspec
from fsspec.spec import AbstractFileSystem

from ._trace_helpers import ensure_trace_dir


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


class JudgmentDetails(TypedDict):
    verdict: int
    yes_count: int
    no_count: int
    all_yes_final_votes: List[Optional[bool]]
    all_no_final_votes: List[Optional[bool]]


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

    def __init__(self, cfg: Dict, env_path: Optional[str] = None):
        if env_path:
            logger.info(f"Loading environment variables from {env_path}")
            env_file_path = find_dotenv(
                env_path, usecwd=True, raise_error_if_not_found=False
            )
            if env_file_path:
                load_dotenv(dotenv_path=env_file_path, override=True)

        self.models: List[str] = cfg.get("models", ["openai/gpt-4o"])
        self.k: int = cfg.get("calls_per_model_per_claim", 3)
        self.temperature: float = cfg.get("temperature", 0.7)
        self.template: str = cfg.get("template", DEFAULT_TEMPLATE)
        self.resolved_cfg: Dict[str, Any] = cfg
        self.current_trace_filepath = self.create_trace_filepath()

        # Ensure models is a list
        if isinstance(self.models, str):
            self.models = [self.models]

    def create_trace_filepath(self):
        trace_dir = ensure_trace_dir()
        if trace_dir:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            return trace_dir / f"{timestamp}.jsonl"

        logger.warning("Trace directory not found. Trace will not be saved.")
        return None

    async def _call_llm(self, model: str, prompt: str) -> Union[str, Exception]:
        """Make a single LLM call and return the response."""
        try:
            response = await litellm.acompletion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            return e

    def _extract_verdict(
        self, llm_output: Union[str, Exception]
    ) -> Tuple[Optional[bool], Optional[str], Optional[str]]:
        """Extract true/false verdict and reasoning from LLM response."""
        if isinstance(llm_output, Exception):
            return None, None, str(llm_output)  # Return error message

        response_text = llm_output  # It's a string here
        if not response_text:
            return None, None, "Empty response from LLM."  # Return error message

        reasoning_text: Optional[str] = None
        verdict: Optional[bool] = None

        reasoning_match = re.search(
            r"<reasoning>\s*(.*?)\s*</reasoning>",
            response_text,
            re.IGNORECASE | re.DOTALL,
        )
        if reasoning_match:
            reasoning_text = reasoning_match.group(1).strip()

        result_section_match = re.search(
            r"<result>\s*(.*?)\s*</result>", response_text, re.IGNORECASE | re.DOTALL
        )

        text_to_parse_for_verdict = response_text  # Default to full response
        if result_section_match:
            text_to_parse_for_verdict = result_section_match.group(1).lower().strip()

        if any(
            word in text_to_parse_for_verdict
            for word in ["true", "yes", "correct", "valid"]
        ):
            verdict = True
        elif any(
            word in text_to_parse_for_verdict
            for word in ["false", "no", "incorrect", "invalid"]
        ):
            verdict = False

        return verdict, reasoning_text, None

    async def _get_model_votes(
        self,
        model: str,
        yes_prompt: str,
        no_prompt: str,
        trace_events: Optional[List[Dict[str, Any]]],
        trace_id: str,
    ) -> Tuple[
        List[Optional[bool]], List[Optional[bool]]
    ]:  # Return type is List of verdicts
        """Get k votes from a single model for both claims."""
        yes_tasks = [self._call_llm(model, yes_prompt) for _ in range(self.k)]
        no_tasks = [self._call_llm(model, no_prompt) for _ in range(self.k)]

        raw_yes_responses = await asyncio.gather(*yes_tasks, return_exceptions=True)
        raw_no_responses = await asyncio.gather(*no_tasks, return_exceptions=True)

        yes_verdicts: List[Optional[bool]] = []
        no_verdicts: List[Optional[bool]] = []

        # Process and trace yes_claim responses
        for i, resp_content_or_exc in enumerate(raw_yes_responses):
            parsed_verdict, reasoning, error_msg = self._extract_verdict(
                resp_content_or_exc
            )
            yes_verdicts.append(parsed_verdict)
            if trace_events is not None:
                event_data = {
                    "trace_id": trace_id,
                    "timestamp": datetime.datetime.now(
                        datetime.timezone.utc
                    ).isoformat(),
                    "type": "llm_response_evaluation",
                    "model": model,
                    "claim_type": "yes",
                    "attempt_k_index": i,
                }
                if error_msg:  # This includes LLM call errors or parsing issues
                    event_data.update({"status": "failure", "error_message": error_msg})
                else:
                    event_data.update(
                        {
                            "status": "success",
                            "raw_response": str(resp_content_or_exc),
                            "parsed_verdict": parsed_verdict,
                            "reasoning_text": reasoning,
                        }
                    )
                trace_events.append(event_data)

        # Process and trace no_claim responses
        for i, resp_content_or_exc in enumerate(raw_no_responses):
            parsed_verdict, reasoning, error_msg = self._extract_verdict(
                resp_content_or_exc
            )
            no_verdicts.append(parsed_verdict)
            if trace_events is not None:
                event_data = {
                    "trace_id": trace_id,
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "type": "llm_response_evaluation",
                    "model": model,
                    "claim_type": "no",
                    "attempt_k_index": i,
                }
                if error_msg:
                    event_data.update({"status": "failure", "error_message": error_msg})
                else:
                    event_data.update(
                        {
                            "status": "success",
                            "raw_response": str(resp_content_or_exc),
                            "parsed_verdict": parsed_verdict,
                            "reasoning_text": reasoning,
                        }
                    )
                trace_events.append(event_data)

        all_responses = raw_yes_responses + raw_no_responses
        critical_error = next(
            (r for r in all_responses if isinstance(r, Exception) and r), None
        )
        if critical_error:
            # This specific error is re-raised to halt if keys are definitively bad.
            raise ValueError(
                f"Critical API key error encountered with {model}: {critical_error}"
            ) from critical_error

        return yes_verdicts, no_verdicts

    # MODIFIED to return discarded_count and accept List[Optional[bool]]
    def _apply_xor_sanity(
        self, yes_votes: List[Optional[bool]], no_votes: List[Optional[bool]]
    ) -> Tuple[
        List[Optional[bool]], List[Optional[bool]], int
    ]:  # Added int for discarded_count
        """Apply XOR sanity check: discard samples that answer both claims the same."""
        filtered_yes: List[Optional[bool]] = []
        filtered_no: List[Optional[bool]] = []
        discarded_count = 0

        for y, n in zip(yes_votes, no_votes):
            if y is None or n is None:
                # Keep samples where at least one is None (abstention/error)
                filtered_yes.append(y)
                filtered_no.append(n)
            elif y != n:
                # Keep samples where answers differ (expected behavior)
                filtered_yes.append(y)
                filtered_no.append(n)
            else:
                # Discard samples where y == n (both True or both False)
                logger.warning(
                    f"Discarding sample (yes_vote={y}, no_vote={n}) due to XOR sanity fail."
                )
                discarded_count += 1

        return filtered_yes, filtered_no, discarded_count

    async def _async_yes_no(
        self,
        yes_prompt: str,
        no_prompt: str,
        trace_events: Optional[List[Dict[str, Any]]],
        trace_id: str,
    ) -> JudgmentDetails:
        """Async implementation of yes_no."""
        all_yes_final_votes: List[Optional[bool]] = []
        all_no_final_votes: List[Optional[bool]] = []

        # Collect votes from all models
        for model in self.models:
            input_yes_verdicts, input_no_verdicts = await self._get_model_votes(
                model,
                yes_prompt,
                no_prompt,
                trace_events,
                trace_id,
            )

            # Apply XOR sanity check per model
            output_yes_verdicts, output_no_verdicts, discarded_pairs = (
                self._apply_xor_sanity(input_yes_verdicts, input_no_verdicts)
            )

            if trace_events is not None:
                trace_events.append(
                    {
                        "trace_id": trace_id,
                        "timestamp": datetime.datetime.now(
                            datetime.timezone.utc
                        ).isoformat(),
                        "type": "model_verdicts_after_xor",
                        "model": model,
                        "input_yes_verdicts_for_model": input_yes_verdicts,
                        "input_no_verdicts_for_model": input_no_verdicts,
                        "output_yes_verdicts_after_xor": output_yes_verdicts,
                        "output_no_verdicts_after_xor": output_no_verdicts,
                        "discarded_pairs_count": discarded_pairs,
                    }
                )

            # If no votes after xor sanity check, skip this model
            if (
                not output_yes_verdicts
                and not output_no_verdicts
                and (input_yes_verdicts or input_no_verdicts)
            ):  # Check if there were input votes
                logger.warning(
                    f"All votes for model {model} were discarded by XOR sanity check."
                )

            all_yes_final_votes.extend(output_yes_verdicts)
            all_no_final_votes.extend(output_no_verdicts)

        # Count votes (None values are abstentions/errors, True is a vote for the claim)
        yes_count = sum(1 for v in all_yes_final_votes if v is True)
        no_count = sum(
            1 for v in all_no_final_votes if v is True
        )  # Count where "NO claim is true"

        # Check if all models abstained or had votes discarded
        # total_votes = len([v for v in all_yes_final_votes + all_no_final_votes if v is not None])
        final_verdict = 1 if yes_count > no_count else 0

        if not any(v is not None for v in all_yes_final_votes + all_no_final_votes):
            logger.warning(
                f"All models in the panel ({', '.join(self.models)}) abstained or had all votes discarded. "
                f"Trace ID: {trace_id}. Final verdict: {final_verdict} (yes_count={yes_count}, no_count={no_count})"
            )
            # Default to 0

        return {
            "verdict": final_verdict,
            "yes_count": yes_count,
            "no_count": no_count,
            "all_yes_final_votes": all_yes_final_votes,
            "all_no_final_votes": all_no_final_votes,
        }

    def yes_no(
        self,
        yes_prompt: str,
        no_prompt: str,
        trace_events: Optional[List[Dict[str, Any]]],
        trace_id: str,
    ) -> JudgmentDetails:
        """
        Evaluate the two prompts and return pass/fail.
        Pass → 1 if YES wins, 0 if NO wins or tie/abstain
        """
        # Run async evaluation using asyncio.run()
        return asyncio.run(
            self._async_yes_no(yes_prompt, no_prompt, trace_events, trace_id)
        )


# ─────────── 3. SINGLETON ENGINE LOADER ──────────────────── #


def _find_config_file_path_for_judge() -> Optional[Path]:
    """Find trainloop.config.yaml, checking TRAINLOOP_CONFIG_PATH env var first."""
    env_config_path_str = os.getenv("TRAINLOOP_CONFIG_PATH")
    if env_config_path_str:
        env_config_path = Path(env_config_path_str)
        if env_config_path.is_file():
            return env_config_path
        else:
            logger.warning(
                f"TRAINLOOP_CONFIG_PATH ('{env_config_path_str}') not found. Trying default locations."
            )

    cwd = Path.cwd()
    # Check common locations relative to CWD
    default_paths = [
        cwd / "trainloop.config.yaml",  # If running from 'trainloop' dir
        cwd / "trainloop" / "trainloop.config.yaml",  # If running from project root
    ]
    for path_candidate in default_paths:
        if path_candidate.is_file():
            return path_candidate

    # Fallback: Search upwards from current directory
    current = cwd
    for _ in range(5):  # Limit search depth
        config_path = current / "trainloop.config.yaml"
        if config_path.is_file():  # Changed from exists() to is_file()
            return config_path
        if current.parent == current:  # Reached filesystem root
            break
        current = current.parent

    logger.warning(
        "Judge config file 'trainloop.config.yaml' not found in standard locations or via TRAINLOOP_CONFIG_PATH."
    )
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
    config_path = _find_config_file_path_for_judge()
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
    cfg_override = json.loads(cfg_override_str) if cfg_override_str else None
    judge_cfg = _load_cfg(cfg_override)
    env_path = judge_cfg.get("env_path")
    return _JudgeEngine(cfg=judge_cfg, env_path=env_path)


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
    """
    trace_id = str(uuid.uuid4())
    trace_events: List[Dict[str, Any]] = []

    cfg_str = json.dumps(cfg, sort_keys=True) if cfg is not None else None
    engine = _engine(cfg_str)

    yes_prompt = make_prompt(yes_claim, engine.template)
    no_prompt = make_prompt(no_claim, engine.template)

    # Initialize judgment_details with a default structure. This is crucial in case
    # engine.yes_no raises an exception before assigning to judgment_details.
    judgment_details: JudgmentDetails = {
        "verdict": 0,  # Default to a non-passing verdict
        "yes_count": 0,
        "no_count": 0,
        "all_yes_final_votes": [],
        "all_no_final_votes": [],
    }

    try:
        # Always append request details if we are tracing (i.e., if trace_events is used)
        trace_events.append(
            {
                "trace_id": trace_id,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                + "Z",
                "type": "judge_request_details",
                "yes_claim": yes_claim,
                "no_claim": no_claim,
                "judge_config": engine.resolved_cfg,
                "yes_prompt": yes_prompt,
                "no_prompt": no_prompt,
            }
        )

        # Pass trace_events list to be populated by engine.yes_no
        judgment_details = engine.yes_no(
            yes_prompt,
            no_prompt,
            trace_events,  # Always pass the list, engine.yes_no appends to it
            trace_id,
        )

    finally:  # Ensure final judgment event and trace log writing occurs
        # Append final judgment details to trace_events first
        # This should happen if judgment_details was successfully populated from the try block
        # or if it retains its initial default values due to an early error in try.
        trace_events.append(
            {
                "trace_id": trace_id,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                + "Z",
                "type": "final_judgment",
                "all_contributing_yes_verdicts": judgment_details.get(
                    "all_yes_final_votes", []  # Use .get for safety
                ),
                "all_contributing_no_verdicts": judgment_details.get(
                    "all_no_final_votes", []  # Use .get for safety
                ),
                "yes_vote_count": judgment_details.get("yes_count", 0),
                "no_vote_count": judgment_details.get("no_count", 0),
                "final_verdict_returned": judgment_details.get("verdict", 0),
            }
        )

        # Now, write all accumulated trace events to the consolidated run log file
        if engine.current_trace_filepath and trace_events:
            try:
                # Ensure parent directory exists using fsspec
                parent_dir = str(engine.current_trace_filepath.parent)
                fs_spec = fsspec.open(str(engine.current_trace_filepath), "a")
                fs = cast(AbstractFileSystem, fs_spec.fs)

                if fs:
                    fs.makedirs(parent_dir, exist_ok=True)

                with fsspec.open(
                    str(engine.current_trace_filepath), "a", encoding="utf-8"
                ) as f:
                    for event in trace_events:
                        json.dump(event, f)  # type: ignore
                        f.write("\n")  # type: ignore
            except Exception as e:
                logger.error(
                    f"Failed to write to consolidated trace log {engine.current_trace_filepath}: {e}"
                )
        elif trace_events and not engine.current_trace_filepath:
            # Log a warning if we have events but no consolidated file path to write them to.
            logger.warning(
                f"Consolidated trace filepath not set for run. Trace events for {trace_id} will not be saved to a run file."
            )

    # Return the verdict from judgment_details.
    # This will be the actual verdict if engine.yes_no completed,
    # or the default (e.g., 0) if an error occurred before it could be set.
    return judgment_details.get("verdict", 0)
