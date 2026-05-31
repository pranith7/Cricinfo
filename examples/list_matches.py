from cricinfo import Cricbuzz


def main() -> None:
    client = Cricbuzz()
    for match in client.matches():
        print(f"{match['id']}: {match['name']}")


if __name__ == "__main__":
    main()
