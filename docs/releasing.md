# Release Process

Cricinfo publishes releases from GitHub releases through PyPI Trusted Publishing.

## Version Policy

The project follows semantic versioning:

- Patch: backward-compatible bug fixes and selector updates.
- Minor: backward-compatible features or new fields.
- Major: breaking public API changes.

## Release Checklist

1. Update `CHANGELOG.md`.
2. Update `cricinfo.__version__` and `project.version` in `pyproject.toml`.
3. Run local checks:

   ```bash
   python -m ruff check .
   python -m mypy cricinfo
   python -m pytest
   python -m build
   ```

4. Create and push a tag:

   ```bash
   git tag v1.3.0
   git push origin v1.3.0
   ```

5. Create a GitHub release from the tag.
6. Confirm the `Release` workflow publishes to PyPI.

## PyPI Trusted Publishing

Configure PyPI with:

- Owner: `pranith7`
- Repository: `Cricinfo`
- Workflow: `release.yml`
- Environment: `pypi`
