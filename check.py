import os
import sys
import urllib.request

URL = "https://ebg-muenchen-west.de/wohnungsangebote/"
NO_OFFERS_TEXT = "keine freien Wohnungen"  # dio rečenice kad nema stanova
STATE_FILE = "state.txt"


def fetch_page() -> str:
    req = urllib.request.Request(
        URL, headers={"User-Agent": "Mozilla/5.0 (apartment-watcher)"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def notify(topic: str) -> None:
    req = urllib.request.Request(
        f"https://ntfy.sh/{topic}",
        data="Moguće nove ponude stanova na EBG München-West!".encode("utf-8"),
        headers={
            "Title": "EBG: novi stanovi?",
            "Click": URL,
            "Priority": "high",
            "Tags": "house",
        },
    )
    urllib.request.urlopen(req, timeout=30)


def read_state() -> str:
    try:
        with open(STATE_FILE) as f:
            return f.read().strip()
    except FileNotFoundError:
        return "none"


def main() -> None:
    topic = os.environ.get("NTFY_TOPIC")
    if not topic:
        sys.exit("NTFY_TOPIC nije postavljen")

    html = fetch_page().lower()

    # Sigurnosna provjera: ako stranica nije normalno učitana, ne diraj stanje
    if "wohnungsangebote" not in html:
        sys.exit("Stranica se nije učitala kako treba")

    state = "none" if NO_OFFERS_TEXT in html else "available"
    previous = read_state()
    print(f"previous={previous} current={state}")

    # Obavijest samo kad se stanje promijeni iz "none" u "available"
    if state == "available" and previous != "available":
        notify(topic)
        print("Obavijest poslana")

    with open(STATE_FILE, "w") as f:
        f.write(state)


if __name__ == "__main__":
    main()
