"""Paper parsing utilities for different input types."""

import re
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

import arxiv
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader

try:
    import pymupdf4llm

    PYMUPDF4LLM_AVAILABLE = True
except ImportError:
    PYMUPDF4LLM_AVAILABLE = False
    pymupdf4llm = None


class PaperParser:
    """Parse papers from various sources."""

    def __init__(self, verbose: bool = False, config: Dict = None):
        self.verbose = verbose
        self.config = config or {}

    def parse(self, source: str) -> Dict[str, str]:
        """Parse paper from source and return structured content."""
        if self._is_arxiv_id(source):
            return self._parse_arxiv(source)
        elif self._is_url(source):
            return self._parse_url(source)
        elif Path(source).is_file():
            return self._parse_file(Path(source))
        else:
            raise ValueError(f"Invalid source: {source}")

    def _is_arxiv_id(self, source: str) -> bool:
        """Check if source is an arXiv ID."""
        arxiv_pattern = r"^\d{4}\.\d{4,5}(v\d+)?$"
        return bool(re.match(arxiv_pattern, source))

    def _is_url(self, source: str) -> bool:
        """Check if source is a URL."""
        try:
            result = urlparse(source)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _parse_arxiv(self, arxiv_id: str) -> Dict[str, str]:
        """Parse paper from arXiv ID."""
        if self.verbose:
            print(f"Fetching arXiv paper: {arxiv_id}")

        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results())

        with tempfile.NamedTemporaryFile(
            suffix=".pdf", delete=False
        ) as tmp_file:
            paper.download_pdf(filename=tmp_file.name)
            content = self._extract_pdf_text(Path(tmp_file.name))

        return {
            "title": paper.title,
            "authors": [str(author) for author in paper.authors],
            "abstract": paper.summary,
            "content": content,
            "source": f"arXiv:{arxiv_id}",
            "url": paper.entry_id,
        }

    def _parse_url(self, url: str) -> Dict[str, str]:
        """Parse paper from URL."""
        if self.verbose:
            print(f"Fetching paper from URL: {url}")

        if "arxiv.org" in url:
            arxiv_id = self._extract_arxiv_id_from_url(url)
            if arxiv_id:
                return self._parse_arxiv(arxiv_id)

        response = requests.get(
            url, headers={"User-Agent": "Winnower/0.1.0"}
        )
        response.raise_for_status()

        if "application/pdf" in response.headers.get("content-type", ""):
            with tempfile.NamedTemporaryFile(
                suffix=".pdf", delete=False
            ) as tmp_file:
                tmp_file.write(response.content)
                content = self._extract_pdf_text(Path(tmp_file.name))

            return {
                "title": self._extract_title_from_url(url),
                "authors": [],
                "abstract": "",
                "content": content,
                "source": url,
                "url": url,
            }
        else:
            soup = BeautifulSoup(response.content, "html.parser")
            return {
                "title": self._extract_title_from_html(soup),
                "authors": [],
                "abstract": "",
                "content": soup.get_text(),
                "source": url,
                "url": url,
            }

    def _parse_file(self, file_path: Path) -> Dict[str, str]:
        """Parse paper from local file."""
        if self.verbose:
            print(f"Parsing file: {file_path}")

        if file_path.suffix.lower() == ".pdf":
            content = self._extract_pdf_text(file_path)
        else:
            content = file_path.read_text(encoding="utf-8", errors="ignore")

        return {
            "title": file_path.stem,
            "authors": [],
            "abstract": "",
            "content": content,
            "source": str(file_path),
            "url": "",
        }

    def _extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from PDF file, with optional markdown conversion."""
        # Check if we should use markdown conversion
        use_markdown = self.config.get("pdf_to_markdown", True)

        if use_markdown and PYMUPDF4LLM_AVAILABLE:
            try:
                if self.verbose:
                    print("Converting PDF to markdown using pymupdf4llm...")
                markdown_text = pymupdf4llm.to_markdown(str(pdf_path))
                return markdown_text
            except Exception as e:
                if self.verbose:
                    print(
                        f"Markdown conversion failed, falling back to "
                        f"text extraction: {e}"
                    )
                # Fall through to legacy extraction
        elif use_markdown and not PYMUPDF4LLM_AVAILABLE:
            if self.verbose:
                print(
                    "pymupdf4llm not available, using legacy PDF extraction"
                )

        # Legacy PyPDF2 extraction
        return self._extract_pdf_text_legacy(pdf_path)

    def _extract_pdf_text_legacy(self, pdf_path: Path) -> str:
        """Legacy PDF text extraction using PyPDF2."""
        try:
            reader = PdfReader(str(pdf_path))
            text = []
            for page in reader.pages:
                text.append(page.extract_text())
            return "\n".join(text)
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not extract text from PDF: {e}")
            return ""

    def _extract_arxiv_id_from_url(self, url: str) -> Optional[str]:
        """Extract arXiv ID from arXiv URL."""
        match = re.search(
            r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", url
        )
        return match.group(1) if match else None

    def _extract_title_from_url(self, url: str) -> str:
        """Extract title from URL."""
        return Path(urlparse(url).path).stem or url

    def _extract_title_from_html(self, soup: BeautifulSoup) -> str:
        """Extract title from HTML."""
        title_tag = soup.find("title")
        return (
            title_tag.get_text().strip() if title_tag else "Unknown Title"
        )

    def find_papers_in_directory(
        self, directory: Path, recursive: bool = False
    ) -> List[Path]:
        """Find paper files in directory."""
        patterns = ["*.pdf", "*.txt", "*.md"]
        files = []

        for pattern in patterns:
            if recursive:
                files.extend(directory.rglob(pattern))
            else:
                files.extend(directory.glob(pattern))

        return sorted(files)
