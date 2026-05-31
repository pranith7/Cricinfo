# Changelog

All notable changes to Cricinfo are documented here.

The project follows semantic versioning.

## [1.3.0] - 2026-05-31

### Added

- Modern `pyproject.toml` packaging with typed package marker.
- Structured return values for matches, summaries, results, live score, commentary, and scorecards.
- Deterministic pytest suite with 90%+ coverage gate.
- Ruff, mypy, Bandit, pip-audit, CodeQL, Dependency Review, and package build automation.
- API reference, examples, contributing guide, security policy, issue templates, and PR template.
- Release workflow for PyPI Trusted Publishing.

### Changed

- Replaced legacy print-only behavior with structured data returns while preserving `print_output=True`.
- Updated Cricbuzz routes to current live-score and scorecard paths.
- Raised supported Python versions to Python 3.10+.

### Security

- Added scheduled dependency and source scanning.
