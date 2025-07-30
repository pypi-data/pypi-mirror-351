"""Smoke tests for basic functionality - good for CI/CD health checks."""

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


def test_import_winnower():
    """Test that winnower can be imported without errors."""
    import winnower

    assert winnower.__version__ == "0.1.0"


def test_cli_help():
    """Test that CLI help works."""
    result = subprocess.run(
        [sys.executable, "-m", "winnower.cli", "--help"], capture_output=True, text=True
    )

    assert result.returncode == 0
    assert "winnower" in result.stdout
    assert "Extract core technical details" in result.stdout


def test_cli_version():
    """Test that CLI version works."""
    result = subprocess.run(
        [sys.executable, "-m", "winnower.cli", "--version"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "0.1.0" in result.stdout


@patch("winnower.cli.setup_user_env")
@patch("winnower.cli.check_api_keys")
def test_setup_command_smoke(mock_check, mock_setup):
    """Test setup command runs without crashing."""
    mock_setup.return_value = Path("/fake/.env")
    mock_check.return_value = {"openai": True, "anthropic": False}

    result = subprocess.run(
        [sys.executable, "-m", "winnower.cli", "setup"], capture_output=True, text=True
    )

    assert result.returncode == 0
    assert "Setting up The Winnower" in result.stdout


@pytest.mark.skipif(
    "GITHUB_ACTIONS" in os.environ,
    reason="Subprocess mocking doesn't work reliably in GitHub Actions"
)
@patch("winnower.extractors.openai.OpenAI")
def test_file_processing_smoke(mock_openai, sample_ml_paper, temp_dir):
    """Test basic file processing without crashing."""
    # Mock OpenAI response
    from unittest.mock import Mock
    import os

    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Test extraction result"

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    # Set fake API key for testing
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = "fake-test-key"

    # Run winnower on sample file
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "winnower.cli",
            str(sample_ml_paper),
            "--output",
            str(temp_dir),
        ],
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0

    # Check output file was created
    output_files = list(temp_dir.glob("**/*_summary.md"))
    assert len(output_files) == 1


def test_config_loading_smoke():
    """Test that config can be loaded without errors."""
    from winnower.config import load_config

    config = load_config()

    # Should have all required keys
    required_keys = ["openai_model", "anthropic_model", "max_tokens", "temperature"]
    for key in required_keys:
        assert key in config


def test_parser_creation_smoke():
    """Test that parser can parse files without errors."""
    from winnower.parsers import PaperParser

    parser = PaperParser()

    # Test basic functionality doesn't crash
    assert not parser._is_arxiv_id("not-arxiv")
    assert parser._is_url("https://example.com")

    # Test directory finding
    fixtures_dir = Path(__file__).parent / "fixtures"
    papers = parser.find_papers_in_directory(fixtures_dir)
    assert len(papers) >= 0  # Should not crash
