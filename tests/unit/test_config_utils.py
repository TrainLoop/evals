"""
Tests for configuration utilities to ensure backward compatibility.
"""

from pathlib import Path
import yaml
from trainloop_cli.commands.utils import load_benchmark_config


class TestBenchmarkConfig:
    """Test benchmark configuration loading and backward compatibility."""

    def test_load_benchmark_config_with_defaults(self, temp_dir: Path):
        """Test loading benchmark config returns defaults when no config exists."""
        config = load_benchmark_config(root_path=temp_dir)

        assert not config["providers"]
        assert config["temperature"] == 0.7
        assert config["max_tokens"] == 1000
        assert config["timeout"] == 60
        assert config["parallel_requests"] == 5
        assert config["env_path"] is None

    def test_load_benchmark_config_from_yaml(self, temp_dir: Path):
        """Test loading benchmark config from YAML file."""
        # Create config with benchmark section
        config_data = {
            "trainloop": {
                "data_folder": "data",
                "benchmark": {
                    "providers": [
                        {"name": "openai", "models": ["gpt-4o", "gpt-4o-mini"]}
                    ],
                    "temperature": 0.5,
                    "max_tokens": 2000,
                    "env_path": "../.env.benchmark",
                },
            }
        }

        config_path = temp_dir / "trainloop.config.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        config = load_benchmark_config(root_path=temp_dir)

        assert len(config["providers"]) == 1
        assert config["providers"][0]["name"] == "openai"
        assert config["providers"][0]["models"] == ["gpt-4o", "gpt-4o-mini"]
        assert config["temperature"] == 0.5
        assert config["max_tokens"] == 2000
        assert config["env_path"] == "../.env.benchmark"
        # Check defaults are still applied for missing fields
        assert config["timeout"] == 60
        assert config["parallel_requests"] == 5

    def test_backward_compatibility_no_benchmark_section(self, temp_dir: Path):
        """Test that configs without benchmark section still work (backward compatibility)."""
        # Create old-style config without benchmark section
        config_data = {
            "trainloop": {
                "data_folder": "data",
                "host_allowlist": ["api.openai.com"],
                "log_level": "info",
                "judge": {
                    "models": ["openai/gpt-4o"],
                    "calls_per_model_per_claim": 3,
                    "temperature": 0.7,
                },
            }
        }

        config_path = temp_dir / "trainloop.config.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        # Should not raise any errors
        config = load_benchmark_config(root_path=temp_dir)

        # Should return defaults
        assert not config["providers"]
        assert config["temperature"] == 0.7
        assert config["max_tokens"] == 1000
        assert config["timeout"] == 60
        assert config["parallel_requests"] == 5
        assert config["env_path"] is None

    def test_partial_benchmark_config(self, temp_dir: Path):
        """Test loading partial benchmark config with some fields missing."""
        config_data = {
            "trainloop": {
                "data_folder": "data",
                "benchmark": {
                    "providers": [
                        {"name": "anthropic", "models": ["claude-3-5-sonnet-20241022"]}
                    ],
                    "temperature": 0.9,
                    # max_tokens, timeout, parallel_requests not specified
                },
            }
        }

        config_path = temp_dir / "trainloop.config.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        config = load_benchmark_config(root_path=temp_dir)

        # Specified values
        assert len(config["providers"]) == 1
        assert config["providers"][0]["name"] == "anthropic"
        assert config["temperature"] == 0.9

        # Default values for unspecified fields
        assert config["max_tokens"] == 1000
        assert config["timeout"] == 60
        assert config["parallel_requests"] == 5
        assert config["env_path"] is None

    def test_empty_trainloop_section(self, temp_dir: Path):
        """Test handling of empty trainloop section."""
        config_data = {"trainloop": {}}

        config_path = temp_dir / "trainloop.config.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        config = load_benchmark_config(root_path=temp_dir)

        # Should return all defaults
        assert config == {
            "providers": [],
            "temperature": 0.7,
            "max_tokens": 1000,
            "timeout": 60,
            "parallel_requests": 5,
            "env_path": None,
        }

    def test_malformed_yaml_returns_defaults(self, temp_dir: Path):
        """Test that malformed YAML doesn't crash, just returns defaults."""
        config_path = temp_dir / "trainloop.config.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("invalid: yaml: content: [[[")

        # Should not raise, just return defaults
        config = load_benchmark_config(root_path=temp_dir)

        assert not config["providers"]
        assert config["temperature"] == 0.7
        assert config["max_tokens"] == 1000
