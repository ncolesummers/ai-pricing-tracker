# Contributing to AI Pricing Tracker

Thank you for your interest in contributing to AI Pricing Tracker! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

- Check if the bug has already been reported in the [Issues](https://github.com/colesummers/ai-pricing-tracker/issues)
- If not, create a new issue with a descriptive title and clear steps to reproduce
- Include as much relevant information as possible (Python version, OS, package version)
- Add screenshots if applicable

### Suggesting Enhancements

- Check if the enhancement has already been suggested in the [Issues](https://github.com/colesummers/ai-pricing-tracker/issues)
- Provide a clear description of the enhancement and its benefits
- If possible, outline how the enhancement could be implemented

### Adding New AI Providers

One of the most valuable contributions is adding support for new AI API providers:

1. Study the existing provider implementations in `scripts/scrape_pricing.py`
2. Create a new method following the pattern: `scrape_<provider>_pricing()`
3. Add appropriate fallback data
4. Update tests in `tests/test_scraper.py`
5. Add the new provider to the README's supported providers list

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/colesummers/ai-pricing-tracker.git
cd ai-pricing-tracker

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests

# Type checking
mypy src
```

## Coding Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use [Black](https://black.readthedocs.io/) for code formatting
- Add type hints to all functions and methods
- Write meaningful docstrings following [Google style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
- Maintain test coverage for all new functionality

## Commit Messages

This project follows [Conventional Commits](https://www.conventionalcommits.org/) for clear, structured commit messages that make the project history readable and enable automated releases.

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation-only changes
- **style**: Changes that don't affect code meaning (formatting, whitespace)
- **refactor**: Code changes that neither fix bugs nor add features
- **perf**: Performance improvements
- **test**: Adding or correcting tests
- **build**: Changes to build system or dependencies
- **ci**: Changes to CI configuration
- **chore**: Other changes that don't modify src or test files

### Scope

Optional scope for specifying the section of the codebase:
- **api**: Changes to the Python API
- **cli**: Command line interface changes
- **scraper**: Price scraping functionality
- **models**: Data models and structures
- **deps**: Dependency updates

### Breaking Changes

Mark breaking changes with `!` and explain in the body:

```
feat(api)!: remove deprecated pricing methods

BREAKING CHANGE: pricing.get_legacy() has been removed in favor of the new pricing.get() method.
```

### Examples

```
feat(scraper): add support for Microsoft Azure OpenAI pricing

- Implement Azure pricing scraper
- Add default fallback pricing
- Update tests and documentation

Closes #42
```

```
fix(models): correct token calculation for Claude models

Fixes incorrect token pricing calculations when context and output have different rates.
```

```
chore(deps): update development dependencies
```

## Release Process

1. Update version in `src/ai_pricing_tracker/__init__.py` and `pyproject.toml`
2. Update `CHANGELOG.md` with the new version and its changes
3. Create a pull request with these changes
4. Once merged, create a new GitHub release and tag

## Questions?

If you have any questions, feel free to open an issue or start a discussion on GitHub.

Thank you for contributing to AI Pricing Tracker!