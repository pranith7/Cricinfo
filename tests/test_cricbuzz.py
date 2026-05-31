import unittest

import requests

from cricinfo import Cricbuzz, CricbuzzError


class FakeResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


class FakeSession:
    def __init__(self, responses):
        self.responses = responses
        self.headers = {}
        self.calls = []

    def get(self, url, timeout):
        self.calls.append((url, timeout))
        return self.responses[url]


class CricbuzzTest(unittest.TestCase):
    def test_matches_returns_unique_structured_matches(self):
        session = FakeSession(
            {
                "https://example.test/": FakeResponse(
                    """
                    <a href="/cricket-commentary/123/india-vs-australia-3rd-odi-123">
                        India vs Australia
                    </a>
                    <a href="/cricket-commentary/123/india-vs-australia-3rd-odi-123">
                        Duplicate
                    </a>
                    <a href="/cricket-commentary/456/england-vs-south-africa-1st-test-456">
                        England vs South Africa
                    </a>
                    """
                )
            }
        )

        client = Cricbuzz(session=session, base_url="https://example.test", timeout=5)

        self.assertEqual(
            client.matches(),
            [
                {
                    "id": "123",
                    "name": "India vs Australia 3rd ODI",
                    "url": "https://example.test/cricket-commentary/123/india-vs-australia-3rd-odi-123",
                },
                {
                    "id": "456",
                    "name": "England vs South Africa 1st Test",
                    "url": "https://example.test/cricket-commentary/456/england-vs-south-africa-1st-test-456",
                },
            ],
        )
        self.assertEqual(session.calls, [("https://example.test/", 5)])

    def test_livescore_parses_optional_sections(self):
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
        session = FakeSession(
            {
                "https://example.test/live-cricket-scores/123": FakeResponse(html),
            }
        )
        client = Cricbuzz(session=session, base_url="https://example.test")

        live = client.livescore("123")

        self.assertEqual(live["header"], "Match 1")
        self.assertEqual(live["status"], "India need 10 runs")
        self.assertEqual(live["team_scores"], "IND 100/2")
        self.assertEqual(live["current_run_rate"], "CRR 7.50")
        self.assertEqual(live["batting"][0]["player"], "R Sharma")
        self.assertEqual(live["bowling"][0]["bowler"], "M Starc")
        self.assertEqual(live["partnership"], "Partnership 30")

    def test_result_falls_back_to_embedded_page_data(self):
        html = r'''
        <script>
        self.__next_f.push(["matchHeader\":{\"matchId\":123,\"status\":\"Match starts at 7:30 PM\"},\"matchScore\":{\"team1Score\":{\"inngs1\":{\"inningsId\":1,\"runs\":200,\"wickets\":4,\"overs\":20}},\"team2Score\":{\"inngs1\":{\"inningsId\":2,\"runs\":190,\"wickets\":8,\"overs\":20}}}"])
        </script>
        '''
        session = FakeSession(
            {
                "https://example.test/live-cricket-scores/123": FakeResponse(html),
            }
        )
        client = Cricbuzz(session=session, base_url="https://example.test")

        self.assertEqual(
            client.result("123"),
            {"result": "Match starts at 7:30 PM", "score": "200/4 (20) | 190/8 (20)"},
        )

    def test_http_errors_raise_package_error(self):
        session = FakeSession(
            {
                "https://example.test/": FakeResponse("missing", status_code=500),
            }
        )
        client = Cricbuzz(session=session, base_url="https://example.test")

        with self.assertRaises(CricbuzzError):
            client.matches()


if __name__ == "__main__":
    unittest.main()
