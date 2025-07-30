"""Core processing logic for The Winnower."""

from pathlib import Path
from typing import Dict, List

from .parsers import PaperParser
from .extractors import TechnicalExtractor
from .formatters import MarkdownFormatter


class WinnowerProcessor:
    """Main processor for extracting technical details from papers."""

    def __init__(
        self,
        config: Dict,
        model_provider: str = "openai",
        verbose: bool = False,
    ):
        self.config = config
        self.verbose = verbose

        self.parser = PaperParser(verbose=verbose, config=config)
        self.extractor = TechnicalExtractor(
            model_provider=model_provider, config=config, verbose=verbose
        )
        self.formatter = MarkdownFormatter()

    def process(
        self, input_source: str, output_dir: Path, recursive: bool = False
    ) -> None:
        """Process papers and generate technical summaries."""
        papers = self._collect_papers(input_source, recursive)

        if not papers:
            print("No papers found to process.")
            return

        output_dir.mkdir(parents=True, exist_ok=True)

        # Create organized directory structure
        papers_dir = output_dir / "papers"
        extracted_dir = output_dir / "extracted"
        summaries_dir = output_dir / "summaries"

        for dir_path in [papers_dir, extracted_dir, summaries_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        for paper_source in papers:
            try:
                if self.verbose:
                    print(f"\nProcessing: {paper_source}")

                paper_data = self.parser.parse(str(paper_source))

                # Save original paper if it's a local file
                source_path = Path(paper_source)
                if source_path.is_file():
                    paper_filename = source_path.name
                    if source_path.suffix.lower() in [".pdf", ".txt", ".md"]:
                        import shutil

                        paper_dest = papers_dir / paper_filename
                        shutil.copy2(source_path, paper_dest)
                        if self.verbose:
                            print(f"Saved original paper: {paper_dest}")

                # Save extracted content
                extracted_filename = self._generate_safe_filename(
                    paper_data["title"], "extracted"
                )
                extracted_file = (
                    extracted_dir / f"{extracted_filename}.md"
                )
                extracted_file.write_text(
                    paper_data["content"], encoding="utf-8"
                )
                if self.verbose:
                    print(f"Saved extracted text: {extracted_file}")

                # Generate and save summary
                technical_content = self.extractor.extract(paper_data)
                markdown_output = self.formatter.format(technical_content)

                summary_filename = self._generate_safe_filename(
                    paper_data["title"], "summary"
                )
                summary_file = summaries_dir / f"{summary_filename}.md"
                summary_file.write_text(markdown_output, encoding="utf-8")

                print(f"Generated summary: {summary_file}")

            except Exception as e:
                print(f"Error processing {paper_source}: {e}")
                if self.verbose:
                    import traceback

                    traceback.print_exc()

    def _collect_papers(self, input_source: str, recursive: bool) -> List[str]:
        """Collect papers to process from input source."""
        source_path = Path(input_source)

        if source_path.is_file():
            return [input_source]
        elif source_path.is_dir():
            files = self.parser.find_papers_in_directory(
                source_path, recursive
            )
            return [str(f) for f in files]
        else:
            return [input_source]

    def _generate_safe_filename(self, title: str, suffix: str = "") -> str:
        """Generate a safe filename from paper title with optional suffix."""
        safe_title = "".join(
            c for c in title if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        safe_title = safe_title.replace(" ", "_")[:50]

        if not safe_title:
            safe_title = "paper"

        if suffix:
            return f"{safe_title}_{suffix}"
        return safe_title
