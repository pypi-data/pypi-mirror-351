"""Unit tests for configuration management."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from winnower.config import load_config, check_api_keys, DEFAULT_CONFIG


class TestConfig:

    def test_default_config(self):
        """Test that default config contains expected keys."""
        assert "openai_model" in DEFAULT_CONFIG
        assert "anthropic_model" in DEFAULT_CONFIG
        assert "max_tokens" in DEFAULT_CONFIG
        assert "temperature" in DEFAULT_CONFIG
        assert "prompt_file" in DEFAULT_CONFIG

    def test_load_config_default(self):
        """Test loading default config."""
        with patch.dict(os.environ, {}, clear=True):
            config = load_config()

        assert config == DEFAULT_CONFIG

    def test_load_config_with_env_vars(self):
        """Test config loading with environment variables."""
        env_vars = {
            "WINNOWER_OPENAI_MODEL": "gpt-3.5-turbo",
            "WINNOWER_MAX_TOKENS": "2000",
            "WINNOWER_TEMPERATURE": "0.5",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config()

        assert config["openai_model"] == "gpt-3.5-turbo"
        assert config["max_tokens"] == 2000
        assert config["temperature"] == 0.5

    def test_load_config_from_file(self):
        """Test loading config from JSON file."""
        test_config = {
            "openai_model": "gpt-4-turbo",
            "max_tokens": 8000,
            "temperature": 0.2,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            config_path = Path(f.name)

        try:
            with patch.dict(os.environ, {}, clear=True):
                config = load_config(config_path)

            assert config["openai_model"] == "gpt-4-turbo"
            assert config["max_tokens"] == 8000
            assert config["temperature"] == 0.2
            # Should still have defaults for unspecified values
            assert config["anthropic_model"] == DEFAULT_CONFIG["anthropic_model"]
        finally:
            config_path.unlink()

    def test_check_api_keys(self):
        """Test API key detection."""
        # Test with OpenAI key
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            status = check_api_keys()
            assert status["openai"] is True
            assert status["anthropic"] is False

        # Test with Anthropic key
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=True):
            status = check_api_keys()
            assert status["openai"] is False
            assert status["anthropic"] is True

        # Test with no keys
        with patch.dict(os.environ, {}, clear=True):
            status = check_api_keys()
            assert status["openai"] is False
            assert status["anthropic"] is False
