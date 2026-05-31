from cricinfo import Cricbuzz, CricbuzzError


def main() -> None:
    client = Cricbuzz(timeout=10)
    matches = client.matches()
    if not matches:
        print("No matches found.")
        return

    match_id = matches[0]["id"]
    print(client.result(match_id))
    print(client.summary(match_id))


if __name__ == "__main__":
    try:
        main()
    except CricbuzzError as exc:
        print(f"Could not fetch match details: {exc}")
