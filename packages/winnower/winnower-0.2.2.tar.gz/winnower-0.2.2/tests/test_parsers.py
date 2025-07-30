"""Unit tests for paper parsers."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from winnower.parsers import PaperParser


class TestPaperParser:

    def setup_method(self):
        self.parser = PaperParser(verbose=False)
        self.fixtures_dir = Path(__file__).parent / "fixtures"

    def test_is_arxiv_id(self):
        """Test arXiv ID detection."""
        assert self.parser._is_arxiv_id("2301.00001")
        assert self.parser._is_arxiv_id("1234.5678")
        assert self.parser._is_arxiv_id("2301.00001v1")
        assert not self.parser._is_arxiv_id("not-arxiv")
        assert not self.parser._is_arxiv_id("2301")
        assert not self.parser._is_arxiv_id("paper.pdf")

    def test_is_url(self):
        """Test URL detection."""
        assert self.parser._is_url("https://example.com/paper.pdf")
        assert self.parser._is_url("http://arxiv.org/abs/2301.00001")
        assert not self.parser._is_url("paper.pdf")
        assert not self.parser._is_url("2301.00001")
        assert not self.parser._is_url("/local/path")

    def test_parse_file(self):
        """Test local file parsing."""
        sample_file = self.fixtures_dir / "sample_ml_paper.txt"
        result = self.parser._parse_file(sample_file)

        assert result["title"] == "sample_ml_paper"
        assert "GradientBoost" in result["content"]
        assert result["source"] == str(sample_file)
        assert result["authors"] == []
        assert result["abstract"] == ""

    def test_find_papers_in_directory(self):
        """Test finding papers in directory."""
        papers = self.parser.find_papers_in_directory(self.fixtures_dir)
        assert len(papers) >= 2  # Should find our test fixtures

        # Check that it finds the specific files we created
        filenames = [p.name for p in papers]
        assert "sample_ml_paper.txt" in filenames
        assert "sample_physics_paper.txt" in filenames

    def test_extract_arxiv_id_from_url(self):
        """Test extracting arXiv ID from URLs."""
        assert (
            self.parser._extract_arxiv_id_from_url("https://arxiv.org/abs/2301.00001")
            == "2301.00001"
        )
        assert (
            self.parser._extract_arxiv_id_from_url("https://arxiv.org/pdf/1234.5678")
            == "1234.5678"
        )
        assert self.parser._extract_arxiv_id_from_url("https://example.com") is None

    @patch("winnower.parsers.arxiv.Search")
    def test_parse_arxiv_mock(self, mock_search):
        """Test arXiv parsing with mocked API."""
        # Mock the arxiv API response
        mock_paper = Mock()
        mock_paper.title = "Test Paper Title"
        mock_paper.authors = [Mock(__str__=lambda x: "John Doe")]
        mock_paper.summary = "Test abstract"
        mock_paper.entry_id = "https://arxiv.org/abs/2301.00001"
        mock_paper.download_pdf = Mock()

        mock_search.return_value.results.return_value = iter([mock_paper])

        with patch.object(
            self.parser, "_extract_pdf_text", return_value="Test content"
        ):
            result = self.parser._parse_arxiv("2301.00001")

        assert result["title"] == "Test Paper Title"
        assert result["authors"] == ["John Doe"]
        assert result["abstract"] == "Test abstract"
        assert result["source"] == "arXiv:2301.00001"
