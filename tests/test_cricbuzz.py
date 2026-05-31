from __future__ import annotations

import pytest

from cricinfo import Cricbuzz, CricbuzzError
from tests.fakes import FakeResponse, FakeSession


def test_constructor_sets_user_agent(base_url: str) -> None:
    session = FakeSession({f"{base_url}/": FakeResponse("")})

    Cricbuzz(session=session, base_url=base_url)

    assert "cricinfo-python" in session.headers["User-Agent"]


def test_matches_returns_unique_structured_matches(base_url: str) -> None:
    session = FakeSession(
        {
            f"{base_url}/": FakeResponse(
                """
                <a href="/live-cricket-scores/123/india-vs-australia-3rd-odi-123">
                    India vs Australia
                </a>
                <a href="/cricket-commentary/123/india-vs-australia-3rd-odi-123">
                    Duplicate
                </a>
                <a href="/live-cricket-scores/456/england-vs-south-africa-1st-test-456">
                    England vs South Africa
                </a>
                """
            )
        }
    )

    client = Cricbuzz(session=session, base_url=base_url, timeout=5)

    assert client.matches() == [
        {
            "id": "123",
            "name": "India vs Australia 3rd ODI",
            "url": f"{base_url}/live-cricket-scores/123/india-vs-australia-3rd-odi-123",
        },
        {
            "id": "456",
            "name": "England vs South Africa 1st Test",
            "url": f"{base_url}/live-cricket-scores/456/england-vs-south-africa-1st-test-456",
        },
    ]
    assert session.calls == [(f"{base_url}/", 5)]


def test_matchinfo_returns_metadata(base_url: str) -> None:
    session = FakeSession(
        {
            f"{base_url}/live-cricket-scorecard/123": FakeResponse(
                """
                <div class="cb-list-item">
                    <h3 class="ui-li-heading">Series</h3>
                    <div class="list-content">World Cup</div>
                </div>
                <div class="cb-list-item">
                    <h3 class="ui-li-heading">Venue</h3>
                    <div class="list-content">Ahmedabad</div>
                </div>
                """
            )
        }
    )

    assert Cricbuzz(session=session, base_url=base_url).matchinfo("123") == {
        "Series": "World Cup",
        "Venue": "Ahmedabad",
    }


def test_matchinfo_can_print_metadata(
    base_url: str, capsys: pytest.CaptureFixture[str]
) -> None:
    session = FakeSession(
        {
            f"{base_url}/live-cricket-scorecard/123": FakeResponse(
                """
                <div class="cb-list-item">
                    <h3 class="ui-li-heading">Venue</h3>
                    <div class="list-content">Ahmedabad</div>
                </div>
                """
            )
        }
    )

    Cricbuzz(session=session, base_url=base_url).matchinfo("123", print_output=True)

    assert "Venue: Ahmedabad" in capsys.readouterr().out


def test_summary_returns_miniscore_data(base_url: str) -> None:
    session = FakeSession(
        {
            f"{base_url}/live-cricket-scores/123": FakeResponse(
                """
                <div class="miniscore-data">IND 100/2</div>
                <div class="miniscore-data">Need 50 from 30</div>
                """
            )
        }
    )

    assert Cricbuzz(session=session, base_url=base_url).summary("123") == [
        "IND 100/2",
        "Need 50 from 30",
    ]


def test_summary_can_print_miniscore_data(
    base_url: str, capsys: pytest.CaptureFixture[str]
) -> None:
    session = FakeSession(
        {
            f"{base_url}/live-cricket-scores/123": FakeResponse(
                '<div class="miniscore-data">IND 100/2</div>'
            )
        }
    )

    Cricbuzz(session=session, base_url=base_url).summary("123", print_output=True)

    assert "IND 100/2" in capsys.readouterr().out


def test_result_uses_legacy_markup_when_available(base_url: str) -> None:
    session = FakeSession(
        {
            f"{base_url}/live-cricket-scores/123": FakeResponse(
                """
                <h3 class="ui-li-heading">India won by 6 wickets</h3>
                <div class="col-xs-9 col-lg-9 dis-inline">IND 201/4</div>
                """
            )
        }
    )

    assert Cricbuzz(session=session, base_url=base_url).result("123") == {
        "result": "India won by 6 wickets",
        "score": "IND 201/4",
    }


def test_result_falls_back_to_embedded_page_data(base_url: str) -> None:
    html = r'''
    <script>
    self.__next_f.push(["matchHeader\":{\"matchId\":123,\"status\":\"Match starts at 7:30 PM\"},\"matchScore\":{\"team1Score\":{\"inngs1\":{\"inningsId\":1,\"runs\":200,\"wickets\":4,\"overs\":20}},\"team2Score\":{\"inngs1\":{\"inningsId\":2,\"runs\":190,\"wickets\":8,\"overs\":20}}}"])
    </script>
    '''
    session = FakeSession({f"{base_url}/live-cricket-scores/123": FakeResponse(html)})

    assert Cricbuzz(session=session, base_url=base_url).result("123") == {
        "result": "Match starts at 7:30 PM",
        "score": "200/4 (20) | 190/8 (20)",
    }


def test_result_raises_when_no_result_data_is_found(base_url: str) -> None:
    session = FakeSession({f"{base_url}/live-cricket-scores/123": FakeResponse("<html />")})

    with pytest.raises(CricbuzzError):
        Cricbuzz(session=session, base_url=base_url).result("123")


def test_result_can_print_data(
    base_url: str, capsys: pytest.CaptureFixture[str]
) -> None:
    session = FakeSession(
        {
            f"{base_url}/live-cricket-scores/123": FakeResponse(
                '<h3 class="ui-li-heading">India won</h3>'
            )
        }
    )

    Cricbuzz(session=session, base_url=base_url).result("123", print_output=True)

    assert "Result of the Match:" in capsys.readouterr().out


def test_livescore_parses_optional_sections(base_url: str) -> None:
    html = """
    <h4 class="cb-list-item ui-header ui-branding-header">Match 1</h4>
    <div class="cbz-ui-status">India need 10 runs</div>
    <div class="miniscore-teams">IND 100/2</div>
    <span class="crr">CRR 7.50</span>
    <table class="table-condensed">
        <tr><th>Batter</th></tr>
        <tr><td>R Sharma</td><td>42</td><td>5</td><td>1</td><td>140.00</td></tr>
    </table>
    <table class="table-condensed">
        <tr><th>Bowler</th></tr>
        <tr><td>M Starc</td><td>4</td><td>0</td><td>25</td><td>1</td></tr>
    </table>
    <div class="ui-branding-style-partner"><div class="list-content">Partnership 30</div></div>
    """
    session = FakeSession({f"{base_url}/live-cricket-scores/123": FakeResponse(html)})

    live = Cricbuzz(session=session, base_url=base_url).livescore("123")

    assert live["header"] == "Match 1"
    assert live["status"] == "India need 10 runs"
    assert live["team_scores"] == "IND 100/2"
    assert live["current_run_rate"] == "CRR 7.50"
    assert live["batting"][0]["player"] == "R Sharma"
    assert live["bowling"][0]["bowler"] == "M Starc"
    assert live["partnership"] == "Partnership 30"


def test_livescore_can_print_sections(
    base_url: str, capsys: pytest.CaptureFixture[str]
) -> None:
    session = FakeSession(
        {
            f"{base_url}/live-cricket-scores/123": FakeResponse(
                """
                <h4 class="cb-list-item ui-header ui-branding-header">Match 1</h4>
                <div class="cbz-ui-status">India need 10 runs</div>
                <div class="miniscore-teams">IND 100/2</div>
                <span class="crr">CRR 7.50</span>
                <table class="table-condensed">
                    <tr><th>Batter</th></tr>
                    <tr><td>R Sharma</td><td>42</td><td>5</td><td>1</td><td>140.00</td></tr>
                </table>
                <table class="table-condensed">
                    <tr><th>Bowler</th></tr>
                    <tr><td>M Starc</td><td>4</td><td>0</td><td>25</td><td>1</td></tr>
                </table>
                <div class="ui-branding-style-partner">
                    <div class="list-content">Partnership 30</div>
                </div>
                """
            )
        }
    )

    Cricbuzz(session=session, base_url=base_url).livescore("123", print_output=True)

    output = capsys.readouterr().out
    assert "Match Header: Match 1" in output
    assert "R Sharma: 42 runs" in output
    assert "M Starc: 4 overs" in output


def test_livescore_handles_missing_tables(base_url: str) -> None:
    session = FakeSession({f"{base_url}/live-cricket-scores/123": FakeResponse("<html />")})

    live = Cricbuzz(session=session, base_url=base_url).livescore("123")

    assert live["batting"] == []
    assert live["bowling"] == []


def test_commentary_returns_clean_items(base_url: str) -> None:
    session = FakeSession(
        {
            f"{base_url}/live-cricket-full-commentary/123": FakeResponse(
                """
                <div class="cb-list-item">
                    <div class="list-content"><span class="commtext">Four! through cover</span></div>
                </div>
                <div class="cb-list-item cbz_ads">
                    <div class="list-content"><span class="commtext">Ad</span></div>
                </div>
                """
            )
        }
    )

    assert Cricbuzz(session=session, base_url=base_url).commentary("123") == [
        "Four! through cover"
    ]


def test_commentary_can_print_items(
    base_url: str, capsys: pytest.CaptureFixture[str]
) -> None:
    session = FakeSession(
        {
            f"{base_url}/live-cricket-full-commentary/123": FakeResponse(
                '<div class="cb-list-item"><div class="list-content">'
                '<span class="commtext">Four! through cover</span></div></div>'
            )
        }
    )

    Cricbuzz(session=session, base_url=base_url).commentary("123", print_output=True)

    assert "Commentary:" in capsys.readouterr().out


def test_scorecard_groups_tables_by_innings(base_url: str) -> None:
    session = FakeSession(
        {
            f"{base_url}/live-cricket-scorecard/123": FakeResponse(
                """
                <div id="inn_1">
                  <div class="cb-list-item ui-header ui-header-small">India Innings</div>
                  <table class="table table-condensed">
                    <tr><th>Batter</th><th>R</th></tr>
                    <tr><td>R Sharma</td><td>42</td></tr>
                  </table>
                </div>
                <div id="inn_2">
                  <div class="cb-list-item ui-header ui-header-small">Australia Innings</div>
                  <table class="table table-condensed">
                    <tr><th>Bowler</th><th>W</th></tr>
                    <tr><td>M Starc</td><td>1</td></tr>
                  </table>
                </div>
                """
            )
        }
    )

    assert Cricbuzz(session=session, base_url=base_url).scorecard("123") == {
        "match_id": "123",
        "innings": [
            {
                "id": "inn_1",
                "teams": ["India Innings"],
                "tables": [[["Batter", "R"], ["R Sharma", "42"]]],
            },
            {
                "id": "inn_2",
                "teams": ["Australia Innings"],
                "tables": [[["Bowler", "W"], ["M Starc", "1"]]],
            },
        ],
    }


def test_scorecard_can_print_tables(
    base_url: str, capsys: pytest.CaptureFixture[str]
) -> None:
    session = FakeSession(
        {
            f"{base_url}/live-cricket-scorecard/123": FakeResponse(
                """
                <div id="inn_1">
                  <div class="cb-list-item ui-header ui-header-small">India Innings</div>
                  <table class="table table-condensed">
                    <tr><th>Batter</th><th>R</th></tr>
                    <tr><td>R Sharma</td><td>42</td></tr>
                  </table>
                </div>
                """
            )
        }
    )

    Cricbuzz(session=session, base_url=base_url).scorecard("123", print_output=True)

    assert "India Innings" in capsys.readouterr().out


def test_print_output_preserves_console_mode(base_url: str, capsys: pytest.CaptureFixture[str]) -> None:
    session = FakeSession(
        {
            f"{base_url}/": FakeResponse(
                '<a href="/live-cricket-scores/123/india-vs-australia-3rd-odi-123">Match</a>'
            )
        }
    )

    Cricbuzz(session=session, base_url=base_url).matches(print_output=True)

    assert "Match Name: India vs Australia 3rd ODI, Match ID: 123" in capsys.readouterr().out


def test_http_errors_raise_package_error(base_url: str) -> None:
    session = FakeSession({f"{base_url}/": FakeResponse("missing", status_code=500)})

    with pytest.raises(CricbuzzError):
        Cricbuzz(session=session, base_url=base_url).matches()
