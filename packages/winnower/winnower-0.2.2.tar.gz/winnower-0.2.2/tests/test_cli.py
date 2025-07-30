"""Tests for CLI interface."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from winnower.cli import main, create_parser, setup_command


class TestCLI:

    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.fixtures_dir = Path(__file__).parent / "fixtures"

    def teardown_method(self):
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parser_creation(self):
        """Test argument parser creation."""
        parser = create_parser()

        # Test help doesn't crash
        help_text = parser.format_help()
        assert "winnower" in help_text
        assert "Extract core technical details" in help_text

    def test_setup_command(self):
        """Test setup command functionality."""
        args = Mock()

        with patch("winnower.cli.setup_user_env") as mock_setup, patch(
            "winnower.cli.check_api_keys"
        ) as mock_check:

            mock_setup.return_value = Path("/fake/path/.env")
            mock_check.return_value = {"openai": True, "anthropic": False}

            result = setup_command(args)

            assert result == 0
            mock_setup.assert_called_once()
            mock_check.assert_called_once()

    @patch("winnower.cli.WinnowerProcessor")
    def test_main_with_file_input(self, mock_processor):
        """Test main function with file input."""
        mock_instance = Mock()
        mock_processor.return_value = mock_instance

        sample_file = str(self.fixtures_dir / "sample_ml_paper.txt")
        argv = [sample_file, "--verbose"]

        result = main(argv)

        assert result == 0
        mock_processor.assert_called_once()
        mock_instance.process.assert_called_once()

    def test_main_setup_command(self):
        """Test main function with setup command."""
        with patch("winnower.cli.setup_command") as mock_setup:
            mock_setup.return_value = 0

            result = main(["setup"])

            assert result == 0
            mock_setup.assert_called_once()

    def test_main_no_input(self):
        """Test main function with no input."""
        result = main([])
        assert result == 1  # Should return error code

    @patch("winnower.cli.WinnowerProcessor")
    def test_main_with_options(self, mock_processor):
        """Test main function with various options."""
        mock_instance = Mock()
        mock_processor.return_value = mock_instance

        sample_file = str(self.fixtures_dir / "sample_ml_paper.txt")
        argv = [
            sample_file,
            "--model",
            "anthropic",
            "--output",
            str(self.temp_dir),
            "--verbose",
        ]

        result = main(argv)

        assert result == 0
        # Check that processor was called with correct arguments
        args, kwargs = mock_processor.call_args
        config, model, verbose = args
        assert model == "anthropic"
        assert verbose is True

    def test_main_keyboard_interrupt(self):
        """Test main function handles keyboard interrupt."""
        with patch("winnower.cli.load_config", side_effect=KeyboardInterrupt):
            result = main(["dummy_input"])
            assert result == 1

    def test_main_exception_handling(self):
        """Test main function handles exceptions."""
        with patch(
            "winnower.cli.load_config", side_effect=Exception("Test error")
        ):
            result = main(["dummy_input"])
            assert result == 1
