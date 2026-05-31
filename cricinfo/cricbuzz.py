"""Small Cricbuzz mobile-site client used by the public Cricinfo package."""

import re
from typing import Any, Dict, Iterable, List, Optional

import requests
from bs4 import BeautifulSoup


class CricbuzzError(RuntimeError):
    """Raised when Cricbuzz cannot be reached or a response cannot be parsed."""


class Cricbuzz:
    """Fetch live cricket data from Cricbuzz's mobile pages.

    Methods return structured Python data and can also print a compact human
    readable view by passing ``print_output=True``.
    """

    BASE_URL = "https://m.cricbuzz.com"
    USER_AGENT = "cricinfo-python/1.3 (+https://github.com/pranith7/cricinfo)"

    def __init__(
        self,
        timeout: int = 10,
        session: Optional[requests.Session] = None,
        base_url: str = BASE_URL,
    ) -> None:
        self.timeout = timeout
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.session.headers.setdefault("User-Agent", self.USER_AGENT)

    def matchinfo(self, mid: Any, print_output: bool = False) -> Dict[str, str]:
        """Return match metadata from a scorecard page."""

        soup = self._soup(f"/live-cricket-scorecard/{mid}")
        data: Dict[str, str] = {}

        for item in soup.find_all("div", class_="cb-list-item"):
            title_element = item.find("h3", class_="ui-li-heading")
            content_element = item.find("div", class_="list-content")
            if title_element and content_element:
                data[self._clean(title_element.get_text())] = self._clean(
                    content_element.get_text()
                )

        if print_output:
            self._print_lines(f"{key}: {value}" for key, value in data.items())

        return data

    def matches(self, print_output: bool = False) -> List[Dict[str, str]]:
        """Return live, recent, and upcoming matches visible on Cricbuzz."""

        soup = self._soup("/")
        pattern = re.compile(r"/(?:live-cricket-scores|cricket-commentary)/(\d+)/([^/#?]+)")
        seen = set()
        matches: List[Dict[str, str]] = []

        for link in soup.find_all("a", href=pattern):
            href = link.get("href")
            if not isinstance(href, str):
                continue
            match = pattern.search(href)
            if not match:
                continue

            match_id = match.group(1)
            if match_id in seen:
                continue

            seen.add(match_id)
            slug = match.group(2).strip("/")
            name = self._title_from_slug(slug)
            matches.append(
                {
                    "id": match_id,
                    "name": name,
                    "url": f"{self.base_url}{href}",
                }
            )

        if print_output:
            self._print_lines(
                f"Match Name: {match['name']}, Match ID: {match['id']}"
                for match in matches
            )

        return matches

    def summary(self, mid: Any, print_output: bool = False) -> List[str]:
        """Return Cricbuzz's mini-score summary for a match."""

        soup = self._soup(f"/live-cricket-scores/{mid}")
        summaries = [
            self._clean(element.get_text())
            for element in soup.find_all(class_="miniscore-data")
        ]

        if print_output:
            self._print_lines(summaries)

        return summaries

    def result(self, mid: Any, print_output: bool = False) -> Dict[str, str]:
        """Return the visible match result/status and score text."""

        html = self._html(f"/live-cricket-scores/{mid}")
        soup = BeautifulSoup(html, "html.parser")
        result = soup.find("h3", class_="ui-li-heading")
        score = soup.find("div", class_="col-xs-9 col-lg-9 dis-inline")

        data = {
            "result": self._clean(result.get_text())
            if result
            else self._embedded_field(html, "status", mid),
            "score": self._clean(score.get_text())
            if score
            else self._embedded_score(html, mid),
        }

        if not any(data.values()):
            raise CricbuzzError(f"Could not find result data for match id {mid}")

        if print_output:
            self._print_lines(["Result of the Match:", data["result"], data["score"]])

        return data

    def livescore(self, mid: Any, print_output: bool = False) -> Dict[str, Any]:
        """Return the current mini-score, batting, and bowling data."""

        soup = self._soup(f"/live-cricket-scores/{mid}")
        data: Dict[str, Any] = {
            "header": self._first_text(
                soup, "h4.cb-list-item.ui-header.ui-branding-header"
            ),
            "status": self._first_text(soup, ".cbz-ui-status"),
            "team_scores": self._first_text(soup, ".miniscore-teams"),
            "current_run_rate": self._first_text(soup, ".crr"),
            "batting": self._table_rows(soup, 0),
            "bowling": self._table_rows(soup, 1),
            "partnership": self._first_text(
                soup, ".ui-branding-style-partner .list-content"
            ),
        }

        if print_output:
            self._print_live_score(data)

        return data

    def commentary(self, mid: Any, print_output: bool = False) -> List[str]:
        """Return recent ball-by-ball commentary."""

        soup = self._soup(f"/live-cricket-full-commentary/{mid}")
        items = [
            self._clean(item.get_text())
            for item in soup.select(".cb-list-item:not(.cbz_ads) .list-content .commtext")
        ]

        if print_output:
            self._print_lines(["Commentary:", *items])

        return items

    def scorecard(self, mid: Any, print_output: bool = False) -> Dict[str, Any]:
        """Return batting and bowling rows grouped by innings."""

        soup = self._soup(f"/live-cricket-scorecard/{mid}")
        innings = []

        for innings_id in ("inn_1", "inn_2"):
            innings_soup = soup.find("div", id=innings_id)
            if not innings_soup:
                continue

            teams = [
                self._clean(team.get_text())
                for team in innings_soup.find_all(
                    "div", class_="cb-list-item ui-header ui-header-small"
                )
            ]
            tables = []
            for table in innings_soup.find_all("table", class_="table table-condensed"):
                rows = []
                for row in table.find_all("tr"):
                    columns = [
                        self._clean(column.get_text())
                        for column in row.find_all(["th", "td"])
                    ]
                    if any(columns):
                        rows.append(columns)
                if rows:
                    tables.append(rows)

            innings.append({"id": innings_id, "teams": teams, "tables": tables})

        data = {"match_id": str(mid), "innings": innings}

        if print_output:
            self._print_scorecard(data)

        return data

    def _soup(self, path: str) -> BeautifulSoup:
        return BeautifulSoup(self._html(path), "html.parser")

    def _html(self, path: str) -> str:
        url = f"{self.base_url}{path}"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise CricbuzzError(f"Failed to fetch {url}: {exc}") from exc

        return response.text

    @staticmethod
    def _clean(value: str) -> str:
        return " ".join(value.split())

    @staticmethod
    def _title_from_slug(slug: str) -> str:
        parts = [part for part in slug.split("-") if not part.isdigit()]
        words = []
        for part in parts:
            if re.fullmatch(r"\d+(st|nd|rd|th)", part):
                words.append(part)
            elif part == "vs":
                words.append("vs")
            elif len(part) <= 3:
                words.append(part.upper())
            else:
                words.append(part.capitalize())

        return " ".join(words)

    def _first_text(self, soup: BeautifulSoup, selector: str) -> str:
        element = soup.select_one(selector)
        return self._clean(element.get_text()) if element else ""

    def _embedded_field(self, html: str, field: str, mid: Optional[Any] = None) -> str:
        if mid is not None:
            for search_area in self._embedded_match_segments(html, mid):
                match = re.search(rf'\\"{field}\\":\\"([^"\\]*)\\"', search_area)
                if match:
                    return self._clean(match.group(1))

        match = re.search(rf'\\"{field}\\":\\"([^"\\]*)\\"', html)
        return self._clean(match.group(1)) if match else ""

    def _embedded_score(self, html: str, mid: Optional[Any] = None) -> str:
        search_areas = [html]
        if mid is not None:
            search_areas = self._embedded_match_segments(html, mid)

        for search_area in search_areas:
            team_scores = []
            for team_number in (1, 2):
                score_match = re.search(
                    rf'\\"team{team_number}Score\\":\{{\\"inngs1\\":\{{'
                    r'\\"inningsId\\":\d+,\\"runs\\":(\d+),\\"wickets\\":(\d+),'
                    r'\\"overs\\":([\d.]+)',
                    search_area,
                )
                if score_match:
                    runs, wickets, overs = score_match.groups()
                    team_scores.append(f"{runs}/{wickets} ({overs})")
            if team_scores:
                return " | ".join(team_scores)

        return ""

    @staticmethod
    def _embedded_match_segments(html: str, mid: Any) -> List[str]:
        marker = rf'\\"matchId\\":{re.escape(str(mid))}'
        marker_matches = list(re.finditer(marker, html))
        segments = []

        for marker_match in marker_matches:
            start = marker_match.start()
            next_match = re.search(r'\\"matchId\\":\d+', html[marker_match.end() :])
            next_start = (
                marker_match.end() + next_match.start()
                if next_match
                else min(len(html), start + 16000)
            )
            segments.append(html[start:next_start])

        return list(reversed(segments))

    def _table_rows(self, soup: BeautifulSoup, table_index: int) -> List[Dict[str, str]]:
        tables = soup.select(".table-condensed")
        if len(tables) <= table_index:
            return []

        rows = []
        for row in tables[table_index].select("tr")[1:]:
            columns = [self._clean(column.get_text()) for column in row.select("td")]
            if not columns:
                continue

            if table_index == 0 and len(columns) >= 5:
                rows.append(
                    {
                        "player": columns[0],
                        "runs": columns[1],
                        "fours": columns[2],
                        "sixes": columns[3],
                        "strike_rate": columns[4],
                    }
                )
            elif table_index == 1 and len(columns) >= 5:
                rows.append(
                    {
                        "bowler": columns[0],
                        "overs": columns[1],
                        "maidens": columns[2],
                        "runs": columns[3],
                        "wickets": columns[4],
                    }
                )

        return rows

    @staticmethod
    def _print_lines(lines: Iterable[str]) -> None:
        for line in lines:
            print(line)

    def _print_live_score(self, data: Dict[str, Any]) -> None:
        if data["header"]:
            print(f"Match Header: {data['header']}\n")
        if data["status"]:
            print(f"Match Status: {data['status']}\n")
        if data["team_scores"]:
            print(f"Team Scores: {data['team_scores']}")
        if data["current_run_rate"]:
            print(f"Current Run Rate: {data['current_run_rate']}")

        if data["batting"]:
            print("\nBatting Details:")
            for batter in data["batting"]:
                print(
                    "{player}: {runs} runs, {fours} fours, {sixes} sixes, "
                    "Strike Rate: {strike_rate}".format(**batter)
                )

        if data["bowling"]:
            print("\nBowling Details:")
            for bowler in data["bowling"]:
                print(
                    "{bowler}: {overs} overs, {maidens} maidens, {runs} runs, "
                    "{wickets} wickets".format(**bowler)
                )

        if data["partnership"]:
            print(f"\nPartner Information:\n{data['partnership']}")

    @staticmethod
    def _print_scorecard(data: Dict[str, Any]) -> None:
        for innings in data["innings"]:
            for team in innings["teams"]:
                print(team)
            print()
            for table in innings["tables"]:
                for row in table:
                    print(" ".join(row))
                print()
