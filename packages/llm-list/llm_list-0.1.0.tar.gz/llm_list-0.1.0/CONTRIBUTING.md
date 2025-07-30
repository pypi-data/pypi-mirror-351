# Contributing to LLM List

First off, thanks for taking the time to contribute! :tada:

The following is a set of guidelines for contributing to LLM List. These are just guidelines, not rules, so use your best judgment and feel free to propose changes to this document in a pull request.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [I don't want to read this whole thing, I just have a question!](#i-dont-want-to-read-this-whole-thing-i-just-have-a-question)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
  - [Pull Requests](#pull-requests)
- [Development Environment](#development-environment)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
  - [Running Tests](#running-tests)
  - [Code Style](#code-style)
- [Additional Notes](#additional-notes)
  - [Issue and Pull Request Labels](#issue-and-pull-request-labels)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## I don't want to read this whole thing, I just have a question!

> **Note:** Please don't file an issue to ask a question. You'll get faster results by using the resources below.

- [GitHub Discussions](https://github.com/yourusername/llm-list/discussions) - Ask and answer questions here
- [GitHub Issues](https://github.com/yourusername/llm-list/issues) - For reporting bugs and feature requests

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check [this list](#before-submitting-a-bug-report) as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible. Fill out the [required template](ISSUE_TEMPLATE/bug_report.md), the information it asks for helps us resolve issues faster.

> **Note:** If you find a **Closed** issue that seems like it is the same thing that you're experiencing, open a new issue and include a link to the original issue in the body of your new one.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for LLM List, including completely new features and minor improvements to existing functionality. Following these guidelines helps maintainers and the community understand your suggestion and find related suggestions.

Before creating enhancement suggestions, please check [this list](#before-submitting-an-enhancement-suggestion) as you might find out that you don't need to create one. When you are creating an enhancement suggestion, please include as many details as possible. Fill in the [template](ISSUE_TEMPLATE/feature_request.md), including the steps that you imagine you would take if the feature you're requesting existed.

### Your First Code Contribution

Unsure where to begin contributing to LLM List? You can start by looking through these `good first issue` and `help wanted` issues:

- [Good first issues](https://github.com/yourusername/llm-list/labels/good%20first%20issue) - issues which should only require a few lines of code, and a test or two.
- [Help wanted issues](https://github.com/yourusername/llm-list/labels/help%20wanted) - issues which should be a bit more involved than `beginner` issues.

### Pull Requests

The process described here has several goals:

- Maintain LLM List's quality
- Fix problems that are important to users
- Engage the community in working toward the best possible LLM List
- Enable a sustainable system for maintainers to review contributions

Please follow these steps to have your contribution considered by the maintainers:

1. Follow all instructions in [the template](.github/PULL_REQUEST_TEMPLATE.md)
2. Follow the [style guides](#code-style)
3. After you submit your pull request, verify that all [status checks](https://help.github.com/articles/about-status-checks/) are passing
   - What if the status checks are failing? If a status check is failing, and you believe that the failure is unrelated to your change, please leave a comment on the pull request explaining why you believe the failure is unrelated. A maintainer will re-run the status check for you. If we conclude that the failure was a false positive, then we will open an issue to track that problem with our status check suite.

While the prerequisites above must be satisfied prior to having your pull request reviewed, the reviewer(s) may ask you to complete additional design work, tests, or other changes before your pull request can be ultimately accepted.

## Development Environment

### Prerequisites

- Python 3.8+
- [Poetry](https://python-poetry.org/) (recommended) or pip
- Git

### Setup

1. Fork the repository on GitHub
2. Clone your fork locally
   ```bash
   git clone https://github.com/yourusername/llm-list.git
   cd llm-list
   ```
3. Install dependencies
   ```bash
   # Using Poetry (recommended)
   poetry install
   
   # Or using pip
   pip install -e ".[dev]"
   ```
4. Run the tests to verify your setup
   ```bash
   make test
   ```

### Running Tests

```bash
# Run all tests
make test

# Run a specific test file
pytest tests/test_ollama_scraper.py -v

# Run tests with coverage report
make coverage
```

### Code Style

This project uses several tools to maintain code quality and style:

- **Black** for code formatting
- **isort** for import sorting
- **mypy** for static type checking
- **flake8** for code linting

Before submitting a pull request, please run:

```bash
make format  # Auto-format code
make lint    # Check code style and type hints
make test    # Run tests
```

## Additional Notes

### Issue and Pull Request Labels

| Label | Description |
|-------|-------------|
| `bug` | Confirmed bugs or reports that are very likely to be bugs |
| `enhancement` | Feature requests |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention is needed |
| `question` | Questions more than bug reports or feature requests |
| `wontfix` | Will not be worked on |
| `duplicate` | Issues that are duplicates of other issues |
| `invalid` | Issues that can't be reproduced or are invalid |
| `documentation` | Improvements or additions to documentation |
| `tests` | Adding missing tests or correcting existing tests |
| `performance` | Performance improvements |
| `security` | Security related issues |

---

Thank you for your interest in contributing to LLM List! Your contributions are greatly appreciated.
