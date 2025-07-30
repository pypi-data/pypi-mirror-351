# 🧺 The Winnower

Provides a technical summary of methods and algorithms from research papers.

## Requirements

- Python 3.8+
- OpenAI API key OR Anthropic API key
- Internet connection for URL/arXiv processing

## Features

The Winnower accepts PDFs, URLs, arXiv IDs, or entire directories of papers. You can adjust the prompt to specialize in physics, machine learning, or whatever you want. It converts PDFs to markdown for better text extraction and uses OpenAI or Anthropic models to identify core technical content. Output summaries focus on methods and algorithms while filtering out background information and experimental results.

## Installation

### With uv (recommended)

```bash
uv add winnower
```

### From PyPI

```bash
pip install winnower
```

### From source

```bash
git clone https://github.com/jwuphysics/winnower.git
cd winnower
pip install -e .
```

## Quick Start

1. Set up The Winnower:
```bash
# Add your API key to .env in the project directory
echo 'OPENAI_API_KEY="your-api-key"' > .env
# OR
echo 'ANTHROPIC_API_KEY="your-api-key"' > .env

# OR set up global configuration
winnower setup  # Creates ~/.winnower/.env template
```

2. Process a paper:
```bash
# From arXiv ID
winnower 2501.00089

# From URL
winnower https://arxiv.org/abs/2501.00089

# From local file
winnower paper.pdf

# Process directory recursively
winnower /path/to/papers/ --recursive
```

## Configuration

The Winnower supports multiple ways to configure API keys and settings:

### API Keys (choose one approach):

1. **Project .env file** (recommended):
```bash
echo 'OPENAI_API_KEY="your-api-key"' > .env
# OR
echo 'ANTHROPIC_API_KEY="your-api-key"' > .env
```

2. **Global .env file** (for personal use):
```bash
winnower setup  # Creates ~/.winnower/.env template
# Edit ~/.winnower/.env and add your API key
```

3. **Environment variables** (for CI/CD, Docker):
```bash
export OPENAI_API_KEY="your-key"
# or
export ANTHROPIC_API_KEY="your-key"
```

### Other Settings

Create `~/.winnower/config.json` for non-sensitive settings:

```json
{
  "openai_model": "gpt-4.1-mini-2025-04-14",
  "anthropic_model": "claude-3-sonnet-20240229",
  "max_tokens": 4000,
  "temperature": 0.1,
  "prompt_file": "/path/to/custom_prompt.txt",
  "pdf_to_markdown": true,
  "summary_length": 200
}
```

Or use environment variables:
- `WINNOWER_OPENAI_MODEL`
- `WINNOWER_ANTHROPIC_MODEL`
- `WINNOWER_MAX_TOKENS`
- `WINNOWER_TEMPERATURE`
- `WINNOWER_PROMPT_FILE`
- `WINNOWER_PDF_TO_MARKDOWN` (true/false)
- `WINNOWER_SUMMARY_LENGTH` (integer, default: 200)

## Output

The Winnower creates an organized directory structure with three folders: `papers/` (original files), `extracted/` (raw text content), and `summaries/` (final technical summaries). The summary files focus on generalizable methods, algorithms, mathematical formulations, and core technical details while ignoring experimental results, background information, and domain-specific applications. Summaries are approximately 200 words by default but can be customized with the `--length` option.

You can customize the extraction behavior with custom prompts using `--prompt-file` or by setting `prompt_file` in your config. The project includes several domain-specific prompts for ML, physics, algorithms, and implementation details. Custom prompt files should include `{title}` and `{content}` placeholders.

## Examples

```bash
# Process single arXiv paper
winnower 2501.00089 -o my_papers/

# Process all PDFs in directory
winnower papers/ --recursive --model anthropic

# Custom config and verbose output
winnower paper.pdf --config my-config.json --verbose

# Longer summary for detailed analysis
winnower paper.pdf --length 500

# Use domain-specific extraction prompts
winnower ml_paper.pdf --prompt-file prompts/ml_focused.txt
winnower physics_paper.pdf --prompt-file prompts/physics_focused.txt

# Disable PDF to markdown conversion (legacy mode)
winnower paper.pdf --no-markdown
```

## Usage

```
winnower [-h] [-o OUTPUT] [-r] [--config CONFIG] [--model {openai,anthropic}]
         [--prompt-file PROMPT_FILE] [--verbose] [--no-markdown] [--length WORDS]
         [--version] [input]
```

**Arguments:**
- `input` - Paper input: file path, directory, URL, or arXiv ID

**Options:**
- `-o, --output OUTPUT` - Output directory (default: ./winnower_output)
- `-r, --recursive` - Process directory recursively
- `--config CONFIG` - Configuration file path
- `--model {openai,anthropic}` - AI model provider (default: openai)
- `--prompt-file PROMPT_FILE` - Custom extraction prompt file
- `--verbose, -v` - Enable verbose output
- `--no-markdown` - Disable PDF to markdown conversion (use legacy text extraction)
- `--length WORDS` - Target length for technical summary in words (default: 200)
- `--version` - Show program version number and exit

## Development

To contribute to The Winnower:

```bash
# Clone and setup
git clone https://github.com/jwuphysics/winnower.git
cd winnower
uv venv && source .venv/bin/activate
uv pip install -e .[dev,test]

# Run tests
make test           # All tests
make test-smoke     # Quick functionality check
make test-unit      # Unit tests only

# Code quality
make format         # Format with black
make lint          # Run flake8 and mypy

# Create .env with test keys for development
cp .env.example .env
# Edit .env with your API keys
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run tests and ensure they pass (`make test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

MIT