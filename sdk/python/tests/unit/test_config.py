"""
Unit tests for config loading functionality.
"""

import os
from pathlib import Path
import pytest
from trainloop_llm_logging.config import load_config_into_env, resolve_data_folder_path


class TestConfigLoading:
    """Test configuration loading and environment variable handling."""

    @pytest.mark.unit
    def test_load_config_from_file(self, temp_config_file, mock_env_vars):
        """Test loading configuration from a YAML file."""
        # Set config path
        os.environ["TRAINLOOP_CONFIG_PATH"] = temp_config_file

        # Load config
        load_config_into_env()

        # Verify environment variables are set
        assert os.environ.get("TRAINLOOP_DATA_FOLDER") is not None
        assert "api.openai.com" in os.environ.get("TRAINLOOP_HOST_ALLOWLIST", "")
        assert os.environ.get("TRAINLOOP_LOG_LEVEL") == "DEBUG"

    @pytest.mark.unit
    def test_env_vars_take_precedence(self, temp_config_file, mock_env_vars):
        """Test that existing environment variables take precedence over config file."""
        # Set environment variables
        os.environ["TRAINLOOP_DATA_FOLDER"] = "/custom/path"
        os.environ["TRAINLOOP_HOST_ALLOWLIST"] = "custom.api.com"
        os.environ["TRAINLOOP_LOG_LEVEL"] = "INFO"
        os.environ["TRAINLOOP_CONFIG_PATH"] = temp_config_file

        # Load config
        load_config_into_env()

        # Verify env vars were not overridden
        assert os.environ["TRAINLOOP_DATA_FOLDER"] == "/custom/path"
        assert os.environ["TRAINLOOP_HOST_ALLOWLIST"] == "custom.api.com"
        assert os.environ["TRAINLOOP_LOG_LEVEL"] == "INFO"

    @pytest.mark.unit
    def test_missing_data_folder_raises_error(self, mock_env_vars):
        """Test that missing TRAINLOOP_DATA_FOLDER raises an error."""
        with pytest.raises(ValueError, match="TRAINLOOP_DATA_FOLDER not set"):
            load_config_into_env()

    @pytest.mark.unit
    def test_resolve_absolute_path(self):
        """Test resolving absolute data folder paths."""
        result = resolve_data_folder_path("/absolute/path", None, Path.cwd())
        assert result == "/absolute/path"

    @pytest.mark.unit
    def test_resolve_relative_path_with_config(self):
        """Test resolving relative paths when config path is provided."""
        config_path = "/config/dir/trainloop.config.yaml"
        result = resolve_data_folder_path("./data", config_path, Path.cwd())
        assert result == str(Path("/config/dir/data"))

    @pytest.mark.unit
    def test_resolve_relative_path_without_config(self):
        """Test resolving relative paths when no config path is provided."""
        cwd = Path.cwd()
        result = resolve_data_folder_path("./data", None, cwd)
        assert result == str(cwd / "data")

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_empty_data_folder_path(self):
        """Test handling of empty data folder path."""
        result = resolve_data_folder_path("", None, Path.cwd())
        assert result == ""

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_config_file_not_found(self, mock_env_vars, temp_data_dir):
        """Test behavior when config file doesn't exist."""
        os.environ["TRAINLOOP_CONFIG_PATH"] = str(
            Path(temp_data_dir) / "nonexistent.yaml"
        )

        with pytest.raises(ValueError):
            load_config_into_env()

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_malformed_yaml_config(self, mock_env_vars, temp_data_dir):
        """Test behavior with malformed YAML."""
        config_path = Path(temp_data_dir) / "bad.yaml"
        config_path.write_text("{ invalid: yaml: content", encoding="utf-8")
        os.environ["TRAINLOOP_CONFIG_PATH"] = str(config_path)

        with pytest.raises(ValueError):
            load_config_into_env()

    @pytest.mark.unit
    def test_auto_discovery_in_trainloop_dir(self, mock_env_vars, temp_data_dir):
        """Test auto-discovery of config in trainloop directory."""
        # Create trainloop directory structure
        trainloop_dir = Path(temp_data_dir) / "trainloop"
        trainloop_dir.mkdir()
        config_file = trainloop_dir / "trainloop.config.yaml"
        config_file.write_text(
            """
trainloop:
  data_folder: ./test-data
  log_level: warn
""",
            encoding="utf-8",
        )

        # Change to temp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_data_dir)
            load_config_into_env()

            assert "test-data" in os.environ.get("TRAINLOOP_DATA_FOLDER", "")
            assert os.environ.get("TRAINLOOP_LOG_LEVEL") == "WARN"
        finally:
            os.chdir(original_cwd)
