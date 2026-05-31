# API Reference

`cricinfo` exposes a single client class:

```python
from cricinfo import Cricbuzz

client = Cricbuzz(timeout=10)
```

## Constructor

```python
Cricbuzz(timeout=10, session=None, base_url="https://m.cricbuzz.com")
```

| Parameter | Type | Description |
| --- | --- | --- |
| `timeout` | `int` | Per-request timeout in seconds. |
| `session` | `requests.Session | None` | Optional session for connection reuse or test fakes. |
| `base_url` | `str` | Override for tests or mirrors. |

## Methods

### `matches(print_output=False)`

Returns live, recent, and upcoming matches from the Cricbuzz landing page.

```python
[
    {
        "id": "155409",
        "name": "RCB vs GT Final Indian Premier League",
        "url": "https://m.cricbuzz.com/live-cricket-scores/155409/...",
    }
]
```

### `matchinfo(match_id, print_output=False)`

Returns match metadata from the scorecard page.

```python
{"Series": "Indian Premier League 2026", "Venue": "Ahmedabad"}
```

### `summary(match_id, print_output=False)`

Returns summary strings from the live-score page.

```python
["IND 100/2", "Need 50 from 30"]
```

### `result(match_id, print_output=False)`

Returns the visible status/result and compact score text.

```python
{"result": "Match starts at May 31, 14:00 GMT", "score": "213/4 (20) | 182/10 (19.4)"}
```

### `livescore(match_id, print_output=False)`

Returns current mini-score data when Cricbuzz exposes it in the page.

```python
{
    "header": "India vs Australia",
    "status": "India need 10 runs",
    "team_scores": "IND 100/2",
    "current_run_rate": "CRR 7.50",
    "batting": [{"player": "R Sharma", "runs": "42"}],
    "bowling": [{"bowler": "M Starc", "overs": "4"}],
    "partnership": "Partnership 30",
}
```

### `commentary(match_id, print_output=False)`

Returns recent commentary strings.

```python
["Four! through cover", "Single to long-on"]
```

### `scorecard(match_id, print_output=False)`

Returns scorecard rows grouped by innings.

```python
{
    "match_id": "155409",
    "innings": [
        {
            "id": "inn_1",
            "teams": ["India Innings"],
            "tables": [[["Batter", "R"], ["R Sharma", "42"]]],
        }
    ],
}
```

## Errors

Network and parsing failures raise `CricbuzzError`.

```python
from cricinfo import Cricbuzz, CricbuzzError

try:
    print(Cricbuzz().matches())
except CricbuzzError as exc:
    print(f"Could not fetch data: {exc}")
```

## Compatibility Mode

Every public method accepts `print_output=True` to print the same style of console output expected by older scripts while still returning structured data.
