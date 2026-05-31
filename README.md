# Cricinfo

A small Python interface for live cricket scores, commentary, match summaries, and scorecards from Cricbuzz.

[![CI](https://github.com/pranith7/Cricinfo/actions/workflows/ci.yml/badge.svg)](https://github.com/pranith7/Cricinfo/actions/workflows/ci.yml)
[![Security](https://github.com/pranith7/Cricinfo/actions/workflows/security.yml/badge.svg)](https://github.com/pranith7/Cricinfo/actions/workflows/security.yml)

```bash
pip install cricinfo
```

## Quick Start

```python
from cricinfo import Cricbuzz

cricket = Cricbuzz()

matches = cricket.matches()
first_match = matches[0]

print(first_match["name"], first_match["id"])
print(cricket.result(first_match["id"]))
```

Every method returns regular Python data, so it is easy to use in scripts, notebooks, APIs, and dashboards.

## Examples

### List Matches

```python
from cricinfo import Cricbuzz

cricket = Cricbuzz()

for match in cricket.matches():
    print(match["id"], match["name"])
```

Returned shape:

```python
[
    {
        "id": "12345",
        "name": "India vs Australia 3rd ODI",
        "url": "https://m.cricbuzz.com/cricket-commentary/12345/...",
    }
]
```

### Match Result

```python
result = cricket.result("12345")

print(result["result"])
print(result["score"])
```

### Live Score

```python
live = cricket.livescore("12345")

print(live["status"])
print(live["team_scores"])
print(live["current_run_rate"])
print(live["batting"])
print(live["bowling"])
```

### Commentary

```python
for item in cricket.commentary("12345"):
    print(item)
```

### Scorecard

```python
scorecard = cricket.scorecard("12345")

for innings in scorecard["innings"]:
    print(innings["teams"])
    print(innings["tables"])
```

### Human-Readable Printing

If you want the older console-style output, pass `print_output=True`.

```python
cricket.matches(print_output=True)
cricket.livescore("12345", print_output=True)
cricket.scorecard("12345", print_output=True)
```

## API

```python
cricket = Cricbuzz(timeout=10)
```

Available methods:

| Method | Returns |
| --- | --- |
| `matches()` | List of match dictionaries with `id`, `name`, and `url` |
| `matchinfo(match_id)` | Match metadata dictionary |
| `summary(match_id)` | List of summary strings |
| `result(match_id)` | Dictionary with `result` and `score` |
| `livescore(match_id)` | Dictionary with status, scores, batting, bowling, and partnership data |
| `commentary(match_id)` | List of commentary strings |
| `scorecard(match_id)` | Dictionary containing innings, teams, and scorecard table rows |

Network and parsing errors raise `CricbuzzError`.

```python
from cricinfo import Cricbuzz, CricbuzzError

try:
    print(Cricbuzz().matches())
except CricbuzzError as exc:
    print(f"Could not fetch Cricbuzz data: {exc}")
```

## Development

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m mypy cricinfo
python -m pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contributor workflow and [docs/api.md](docs/api.md) for API details.

Release history is tracked in [CHANGELOG.md](CHANGELOG.md), and upcoming work is tracked in [ROADMAP.md](ROADMAP.md).

## Notes

This package scrapes Cricbuzz's public mobile pages. Page structure changes on Cricbuzz can require selector updates.
