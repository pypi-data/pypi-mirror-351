"""Technical content extraction using AI models."""

import os
import re
from pathlib import Path
from typing import Dict

try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None


class TechnicalExtractor:
    """Extract technical content from papers using AI models."""

    DEFAULT_EXTRACTION_PROMPT = """
You are a technical reviewer tasked with extracting ONLY the core
technical details from a research paper. Create EXTREMELY CONCISE summaries
focusing EXCLUSIVELY on generalizable methods, algorithms, and advancements.

For ML/Statistics/Applied Math papers, extract ONLY:
1. **Core Algorithms**: Essential algorithmic procedures without
   implementation details
2. **Mathematical Formulations**: Key equations and theoretical
   foundations
3. **Technical Methods**: Novel approaches described at the
   conceptual level
4. **Critical Parameters**: Only absolutely essential hyperparameters

For Physics/Astronomy papers, extract ONLY:
1. **Mathematical Formulations**: Essential equations without
   derivations
2. **Conceptual Methods**: Core theoretical frameworks without
   applications
3. **Physical Models**: Fundamental mathematical descriptions in
   abstract form
4. **Critical Parameters**: Only absolutely essential physical
   constants

YOU MUST STRICTLY IGNORE:
- ALL applications and use cases
- ALL benchmarks and comparisons
- ALL experimental results and metrics
- ALL marketing language and promotional content
- ALL background information and literature review
- ALL implementation details unless fundamentally novel
- ALL domain-specific adaptations

Create the MOST CONCISE output possible using minimal text. Focus EXCLUSIVELY
on generalizable technical content that transfers directly to other problems
or domains.

Paper Title: {title}

Paper Content:
{content}

Extract ONLY the core technical details following the guidelines
above. Limit your response to approximately {length} words:
"""

    def __init__(
        self,
        model_provider: str = "openai",
        config: Dict = None,
        verbose: bool = False,
    ):
        self.model_provider = model_provider
        self.config = config or {}
        self.verbose = verbose
        self.extraction_prompt = self._load_extraction_prompt()

        if model_provider == "openai":
            if not openai:
                raise ImportError(
                    "OpenAI package not installed. Run: pip install openai"
                )
            self.client = openai.OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
        elif model_provider == "anthropic":
            if not anthropic:
                raise ImportError(
                    "Anthropic package not installed. "
                    "Run: pip install anthropic"
                )
            self.client = anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        else:
            raise ValueError(f"Unsupported model provider: {model_provider}")

    def extract(self, paper_data: Dict) -> Dict:
        """Extract technical content from paper data."""
        if self.verbose:
            print("Extracting technical content...")

        content = self._preprocess_content(paper_data["content"])

        if len(content) > 100000:
            content = (
                content[:100000] + "\n[Content truncated for processing]"
            )

        technical_content = self._extract_with_ai(
            paper_data["title"], content
        )

        return {
            "title": paper_data["title"],
            "authors": paper_data["authors"],
            "source": paper_data["source"],
            "url": paper_data["url"],
            "abstract": paper_data["abstract"],
            "technical_content": technical_content,
        }

    def _preprocess_content(self, content: str) -> str:
        """Clean and preprocess paper content."""
        content = re.sub(r"\n+", "\n", content)
        content = re.sub(r"\s+", " ", content)

        sections_to_remove = [
            r"References\s*\n.*",
            r"Bibliography\s*\n.*",
            r"Acknowledgments?\s*\n.*",
            r"Appendix\s*[A-Z]?\s*\n.*",
        ]

        for pattern in sections_to_remove:
            content = re.sub(
                pattern, "", content, flags=re.DOTALL | re.IGNORECASE
            )

        return content.strip()

    def _load_extraction_prompt(self) -> str:
        """Load extraction prompt from config or use default."""
        prompt_file = self.config.get("prompt_file")
        if prompt_file and Path(prompt_file).exists():
            if self.verbose:
                print(f"Loading custom prompt from: {prompt_file}")
            return Path(prompt_file).read_text(encoding="utf-8")

        custom_prompt = self.config.get("extraction_prompt")
        if custom_prompt:
            if self.verbose:
                print("Using custom prompt from config")
            return custom_prompt

        return self.DEFAULT_EXTRACTION_PROMPT

    def _extract_with_ai(self, title: str, content: str) -> str:
        """Extract technical content using AI model."""
        prompt = self.extraction_prompt.format(
            title=title, 
            content=content,
            length=self.config.get("summary_length", 200)
        )

        if self.model_provider == "openai":
            return self._extract_with_openai(prompt)
        elif self.model_provider == "anthropic":
            return self._extract_with_anthropic(prompt)

    def _extract_with_openai(self, prompt: str) -> str:
        """Extract using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.config.get("openai_model", "gpt-4"),
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a technical reviewer extracting "
                            "core technical details from research papers."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.config.get("max_tokens", 4000),
                temperature=self.config.get("temperature", 0.1),
            )
            return response.choices[0].message.content
        except Exception as e:
            if self.verbose:
                print(f"OpenAI API error: {e}")
            return f"Error extracting technical content: {e}"

    def _extract_with_anthropic(self, prompt: str) -> str:
        """Extract using Anthropic API."""
        try:
            response = self.client.messages.create(
                model=self.config.get(
                    "anthropic_model", "claude-3-sonnet-20240229"
                ),
                max_tokens=self.config.get("max_tokens", 4000),
                temperature=self.config.get("temperature", 0.1),
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:
            if self.verbose:
                print(f"Anthropic API error: {e}")
            return f"Error extracting technical content: {e}"
