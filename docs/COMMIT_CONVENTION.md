# Conventional Commits Guide

AI Pricing Tracker follows the [Conventional Commits](https://www.conventionalcommits.org/) specification for creating clear, structured commit messages. This document provides comprehensive examples and guidance.

## Commit Message Structure

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Commit Types

| Type | Description | Example |
|------|-------------|---------|
| feat | New features or significant additions | `feat: add support for Google Vertex AI pricing` |
| fix | Bug fixes | `fix: correct output token calculation for GPT-4` |
| docs | Documentation changes | `docs: update installation instructions` |
| style | Formatting changes (not affecting code functionality) | `style: fix indentation in pricing module` |
| refactor | Code restructuring without feature changes | `refactor: simplify pricing data loading logic` |
| perf | Performance improvements | `perf: optimize model cost calculation` |
| test | Adding or updating tests | `test: add unit tests for Azure pricing` |
| build | Changes to build system or dependencies | `build: update playwright requirement` |
| ci | CI configuration changes | `ci: add GitHub Action for daily price updates` |
| chore | Maintenance tasks | `chore: update copyright year` |

## Scopes

Scope should be a noun describing the section of the codebase:

| Scope | Description |
|-------|-------------|
| api | Python API functionality |
| cli | Command-line interface |
| scraper | Web scraping components |
| models | Data models and structures |
| deps | Dependencies and requirements |
| config | Configuration handling |

## Examples for All Types

### Features

```
feat(scraper): add support for Cohere pricing

- Implement Cohere pricing scraper
- Add default fallback pricing data
- Update documentation with Cohere models

Closes #123
```

### Bug Fixes

```
fix(models): correct token calculation for Claude models

Fixes incorrect token pricing calculations when context and output 
have different rates.

Fixes #456
```

### Documentation

```
docs: improve installation instructions

- Add troubleshooting section
- Clarify Python version requirements
- Add screenshots for CLI examples
```

### Style Changes

```
style: improve code formatting

- Apply consistent indentation
- Remove trailing whitespace
- Fix line length issues
```

### Refactoring

```
refactor(api): simplify caching mechanism

Replace custom caching with functools.lru_cache for better 
maintainability and performance.
```

### Performance Improvements

```
perf: optimize pricing data loading

Reduce startup time by 40% by lazy-loading provider data
only when needed.
```

### Tests

```
test: expand test coverage for manager module

- Add tests for edge cases
- Improve test fixture organization
- Mock external dependencies consistently
```

### Build System

```
build(deps): update dependencies

- Update playwright to v1.32.0
- Update pytest to v7.3.1
- Pin black version for consistency
```

### CI Configuration

```
ci: add automated release workflow

Add GitHub Action to automate package building and PyPI release
when a new version tag is pushed.
```

### Chores

```
chore: clean up temporary files

Remove cached files and update gitignore to prevent future inclusions.
```

## Breaking Changes

Breaking changes should be indicated with `!` after the type/scope and a `BREAKING CHANGE:` footer:

```
feat(api)!: revise pricing API interface

Simplify the interface by merging related methods and standardizing
parameter names.

BREAKING CHANGE: The methods get_token_price() and get_request_price()
have been merged into a single get_price() method with a 'price_type'
parameter.
```

## Tips for Good Commit Messages

1. **Be concise**: Keep the description under 72 characters
2. **Be specific**: Clearly state what changed and why
3. **Use imperative mood**: Write as if giving a command
4. **No period**: Don't end the commit message with a period
5. **Separate subject from body** with a blank line
6. **Explain the why**: The body should explain why the change was necessary
7. **Reference issues**: Include issue/PR numbers when relevant