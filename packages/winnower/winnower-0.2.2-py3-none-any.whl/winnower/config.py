"""Configuration management for The Winnower."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv


DEFAULT_CONFIG = {
    "openai_model": "gpt-4.1-mini-2025-04-14",
    "anthropic_model": "claude-3-sonnet-20240229",
    "max_tokens": 4000,
    "temperature": 0.1,
    "verbose": False,
    "extraction_prompt": None,
    "prompt_file": None,
    "pdf_to_markdown": True,
    "summary_length": 200,
}


def load_config(config_path: Optional[Path] = None) -> Dict:
    """Load configuration from file and environment.

    Priority order for API keys and settings:
    1. Environment variables (highest priority)
    2. Project .env file
    3. Global .env file (~/.winnower/.env)
    4. Config JSON files (lowest priority, non-sensitive only)
    """
    # Load .env files in priority order (later calls don't override
    # existing vars)
    load_dotenv(Path.home() / ".winnower" / ".env")  # Global .env first
    load_dotenv(".env")  # Project .env second (higher priority)

    config = DEFAULT_CONFIG.copy()

    if config_path and config_path.exists():
        with open(config_path, "r") as f:
            file_config = json.load(f)
            config.update(file_config)
    else:
        default_config_path = Path.home() / ".winnower" / "config.json"
        if default_config_path.exists():
            with open(default_config_path, "r") as f:
                file_config = json.load(f)
                config.update(file_config)

    env_overrides = {
        "openai_model": os.getenv("WINNOWER_OPENAI_MODEL"),
        "anthropic_model": os.getenv("WINNOWER_ANTHROPIC_MODEL"),
        "max_tokens": os.getenv("WINNOWER_MAX_TOKENS"),
        "temperature": os.getenv("WINNOWER_TEMPERATURE"),
        "prompt_file": os.getenv("WINNOWER_PROMPT_FILE"),
        "pdf_to_markdown": os.getenv("WINNOWER_PDF_TO_MARKDOWN"),
        "summary_length": os.getenv("WINNOWER_SUMMARY_LENGTH"),
    }

    for key, value in env_overrides.items():
        if value is not None:
            if key in ["max_tokens", "summary_length"]:
                config[key] = int(value)
            elif key in ["temperature"]:
                config[key] = float(value)
            elif key in ["pdf_to_markdown"]:
                config[key] = value.lower() in ("true", "1", "yes", "on")
            else:
                config[key] = value

    return config


def create_default_config(config_dir: Path = None) -> Path:
    """Create default configuration file."""
    if config_dir is None:
        config_dir = Path.home() / ".winnower"

    config_dir.mkdir(exist_ok=True)
    config_path = config_dir / "config.json"

    with open(config_path, "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)

    return config_path


def setup_user_env(config_dir: Path = None) -> Path:
    """Set up user environment directory with .env template."""
    if config_dir is None:
        config_dir = Path.home() / ".winnower"

    config_dir.mkdir(exist_ok=True)
    env_path = config_dir / ".env"

    if not env_path.exists():
        env_template = """# The Winnower Global Configuration
# This file is loaded for all Winnower sessions

# API Keys (required - choose one)
# OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Global Model Preferences (optional)
# WINNOWER_OPENAI_MODEL=gpt-4
# WINNOWER_ANTHROPIC_MODEL=claude-3-sonnet-20240229
# WINNOWER_MAX_TOKENS=4000
# WINNOWER_TEMPERATURE=0.1
"""
        env_path.write_text(env_template)

    return env_path


def check_api_keys() -> Dict[str, bool]:
    """Check which API keys are available."""
    return {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
    }
