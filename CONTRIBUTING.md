# Contributing

Thanks for helping improve Cricinfo. The project is intentionally small, so contributions should keep the public API simple, typed, and well-tested.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Quality Checks

Run these before opening a pull request:

```bash
python -m ruff check .
python -m mypy cricinfo
python -m pytest
python -m bandit -c pyproject.toml -r cricinfo
```

## Pull Request Guidelines

Keep changes focused. Include tests for parser changes and avoid tests that require live Cricbuzz network access. If Cricbuzz changes page structure, add a minimal fixture that captures the relevant HTML shape.

## Versioning

Cricinfo follows semantic versioning:

| Change | Version bump |
| --- | --- |
| Backward-compatible bug fix | Patch |
| Backward-compatible feature | Minor |
| Breaking API change | Major |

## Maintainer Checklist

Before release, verify:

```bash
python -m ruff check .
python -m mypy cricinfo
python -m pytest
python -m build
```
