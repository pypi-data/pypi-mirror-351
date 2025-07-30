# LLM List

[![PyPI](https://img.shields.io/pypi/v/llm-list.svg)](https://pypi.org/project/llm-list/)
[![Python Version](https://img.shields.io/pypi/pyversions/llm-list.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python package to list and monitor available LLM models from various providers including Ollama and Hugging Face.

## Features

- List available LLM models from multiple providers
- Monitor model updates and changes
- Simple and intuitive API
- Caching support for offline usage
- Command-line interface
- Docker support

## Installation

### Using pip

```bash
pip install llm-list
```

### From source

```bash
git clone https://github.com/softreck/llm-list.git
cd llm-list
pip install -e .
```

### Using Docker

```bash
docker build -t llm-list .
docker run --rm -it llm-list --help
```

## Usage

### Command Line Interface

```bash
# List all available models
llm-list list

# List models from a specific provider
llm-list list --provider ollama
llm-list list --provider huggingface

# Save output to a file
llm-list list --output models.json

#### Get help
```bash
llm-list --help
```

### Python API

#### Get Ollama models
```python
from llm_list.scrapers import OllamaScraper

# Create a scraper instance
scraper = OllamaScraper(output_dir="./data")

# Scrape models
models = scraper.scrape_models()
print(f"Found {len(models)} models")

# Monitor for changes
scraper.monitor(interval=3600)  # Check every hour
```

#### Get Hugging Face models
```python
from llm_list.scrapers import HuggingFaceScraper

# Create a scraper instance
scraper = HuggingFaceScraper(output_dir="./data")

# Scrape models with search filter
models = scraper.scrape_models(search_term="code")
print(f"Found {len(models)} models")

# Get default models (works offline)
default_models = scraper._load_cached_models()
```

## Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/llm-list.git
   cd llm-list
   ```

2. Install the package in development mode with all dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Run tests:
   ```bash
   make test
   ```

4. Run linters and type checking:
   ```bash
   make lint
   ```

5. Format code:
   ```bash
   make format
   ```

## Available Make Commands

- `make install` - Install the package in development mode
- `make dev` - Install development dependencies
- `make test` - Run tests
- `make coverage` - Generate and view test coverage report
- `make lint` - Check code style with black, isort, and mypy
- `make format` - Format code with black and isort
- `make typecheck` - Run type checking with mypy
- `make clean` - Remove build artifacts
- `make build` - Build the package
- `make check` - Check the package
- `make publish-test` - Upload to TestPyPI
- `make publish` - Upload to PyPI
- `make pre-commit` - Run all checks before committing
- `make help` - Show available commands

## Publishing to PyPI

1. Update the version number in `setup.py`
2. Update the changelog in `CHANGELOG.md`
3. Build the package:
   ```bash
   make build
   ```
4. Test the package:
   ```bash
   make check
   ```
5. Publish to TestPyPI (optional):
   ```bash
   make publish-test
   ```
6. Publish to PyPI:
   ```bash
   make publish
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
