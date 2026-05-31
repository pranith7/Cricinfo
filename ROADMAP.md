# Roadmap

## Near Term

- Stabilize parser coverage around current Cricbuzz page structures.
- Add typed response models with backward-compatible dictionary serialization.
- Add optional JSON export helpers for dashboards and notebooks.
- Publish signed releases to PyPI through Trusted Publishing.

## Medium Term

- Add async fetching for multi-match dashboards.
- Add richer scorecard parsing for innings, fall of wickets, partnerships, and extras.
- Add integration tests that run on a schedule against a small set of public match pages.
- Add documentation site generation from `docs/`.

## AI-Assisted Features

OpenAI API credits would accelerate useful cricket intelligence features:

- Natural-language match queries over live scorecards and commentary.
- Match summaries tuned for fans, analysts, and fantasy-cricket users.
- Player-form and matchup insights from recent scorecards.
- Commentary clustering into turning points, pressure phases, and momentum shifts.
- Cricket analytics assistant that can answer questions like "why did the chase slow down?"

## Governance

- Keep the core library small and dependency-light.
- Require deterministic tests for all parser changes.
- Treat changes to public return shapes as semver-significant.
- Prefer additive APIs over breaking changes.
