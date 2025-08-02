# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project that integrates LLM capabilities with the PocketSmith API for financial data processing. The project uses:

- **LLM Framework**: `llm` package with Anthropic provider for AI interactions
- **Financial API**: `pocketsmith-api` for accessing PocketSmith financial data
- **Package Management**: Uses `uv` for dependency management (evidenced by `uv.lock`)

## Development Commands

### Environment Setup
```bash
# Install dependencies using uv
uv sync

# Activate virtual environment
source .venv/bin/activate  # or equivalent for your shell
```

### Running the Application
```bash
# Run the main application
python main.py

# Or using uv
uv run python main.py
```

### Development Workflow
Since this project uses `uv` for package management:
- Use `uv add <package>` to add new dependencies
- Use `uv remove <package>` to remove dependencies
- Use `uv sync` to sync dependencies after changes

## Architecture

The project is currently in early development with a minimal structure:
- `main.py`: Entry point with basic setup
- `pyproject.toml`: Project configuration with LLM and PocketSmith API dependencies
- The combination of LLM and PocketSmith suggests this tool processes financial data using AI

## Key Dependencies

- `llm>=0.26`: Core LLM framework for AI interactions
- `llm-anthropic>=0.17`: Anthropic provider for Claude integration
- `pocketsmith-api>=2.1.1`: API client for PocketSmith financial platform

This suggests the project's purpose is to use Claude/LLM capabilities to analyze or process financial data from PocketSmith.