# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Pricing Tracker is a Python package that provides up-to-date pricing information for AI and LLM APIs, including Anthropic, OpenAI, with Google and others planned for future support. The package:

- Auto-updates pricing data daily via GitHub Actions
- Provides both a Python API and CLI for accessing pricing information
- Tracks pricing historically via git history
- Requires zero configuration and no API keys

## Development Commands

### Setup and Installation

```bash
# Clone the repository
git clone https://github.com/colesummers/ai-pricing-tracker.git
cd ai-pricing-tracker

# Create and activate virtual environment (located in .venv)
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev]"
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_manager.py

# Run with verbosity
pytest -v
```

### Code Quality

```bash
# Format code with black
black src tests

# Run flake8 linting
flake8 src tests

# Run type checking with mypy
mypy src tests

# Run all quality checks at once
python -m black . && python -m flake8 && python -m mypy src tests
```

### Building and Publishing

```bash
# Build the package
python -m build

# Upload to PyPI (requires credentials)
twine upload dist/*
```

### Running the Scraper

```bash
# Run the pricing scraper script
python scripts/scrape_pricing.py
```

## Architecture

The package follows a clean, modular architecture:

1. **Core Components**:
   - `PricingManager`: Main interface class that handles loading, caching, and accessing pricing data
   - `PricingData`: Container for all pricing information
   - `ModelPricing`: Represents pricing for a single AI model
   - Custom exceptions for error handling

2. **Data Flow**:
   - Pricing data is fetched from GitHub repository
   - Data is cached locally (~/.ai_pricing_tracker by default)
   - Fallback to bundled data if network unavailable
   - Daily GitHub Actions workflow scrapes latest pricing

3. **CLI Interface**:
   - Provides commands for listing models, getting pricing, calculating costs
   - Command: `ai-pricing-update`

4. **Testing**:
   - Unit tests use pytest
   - Tests cover core functionality with mocked responses

## Key Files

- `src/ai_pricing_tracker/manager.py`: Core pricing manager class
- `src/ai_pricing_tracker/models.py`: Data structures for pricing information
- `src/ai_pricing_tracker/cli.py`: Command-line interface
- `scripts/scrape_pricing.py`: Pricing data scraper using Playwright
- `data/pricing/`: Directory for storing pricing data files

## Development Guidelines

1. **Type Annotations**: 
   - All new code should include type hints
   - Run mypy to verify type correctness

2. **Testing**:
   - All new features should include unit tests
   - Use fixtures and mocks to avoid network dependencies

3. **Error Handling**:
   - Use the custom exception hierarchy in exceptions.py
   - Ensure graceful fallbacks for network/data failures

4. **Data Structure**:
   - Pricing data follows a specific JSON format
   - Model identifiers use format: "provider/model-name"

5. **Commit Guidelines**:
   - Follow [Conventional Commits](https://www.conventionalcommits.org/) format
   - Use format: `type(scope): description`
   - Common types: feat, fix, docs, style, refactor, perf, test, build, ci, chore
   - Include scope when relevant (e.g., api, cli, scraper, models)
   - Mark breaking changes with `!` and a BREAKING CHANGE footer
   - See [Commit Convention Guide](docs/COMMIT_CONVENTION.md) for details