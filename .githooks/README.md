# Git Hooks for AI Pricing Tracker

This directory contains git hooks to help maintain code quality and consistent commit messages.

## Installation

To install the hooks, run the following command from the project root:

```bash
git config core.hooksPath .githooks
chmod +x .githooks/*
```

## Available Hooks

### commit-msg

Validates that commit messages follow the [Conventional Commits](https://www.conventionalcommits.org/) format.

The commit message must:
- Start with a type (feat, fix, docs, etc.)
- Optionally include a scope in parentheses
- Include a colon and space, followed by a description
- Mark breaking changes with `!` before the colon
- Include a `BREAKING CHANGE:` footer for breaking changes

Example valid commit messages:
```
feat(scraper): add support for Microsoft Azure OpenAI pricing
fix: correct token calculation for Claude models
docs: update installation instructions
```

## Pre-commit Integration

If you use [pre-commit](https://pre-commit.com/), you can add this hook to your `.pre-commit-config.yaml` file:

```yaml
repos:
  - repo: local
    hooks:
      - id: conventional-commit-msg
        name: Conventional Commit Message
        entry: .githooks/commit-msg
        language: script
        stages: [commit-msg]
```