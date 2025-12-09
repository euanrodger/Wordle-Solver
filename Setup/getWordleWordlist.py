"""Get list of Wordle words.
"""

"""Code copied (and slightly modified for path purposes) from https://gist.github.com/dmahugh/4546585c1af1e8959e583d933fbc4461#file-wordle_guess-py
Explained here: https://www.dougmahugh.com/wordle-art/
"""

from datetime import datetime
from urllib.parse import urljoin
import re

from bs4 import BeautifulSoup
import requests

from pathlib import Path

WORDLE_URL = "https://www.nytimes.com/games/wordle/"
# Output to WordLists/wordle-words-YYYY-MM-DD.txt in parent directory
FILENAME = str(Path(__file__).parent.parent / "WordLists" / f"wordle-words-{datetime.today().strftime('%Y-%m-%d')}.txt")


def main():
    """Get the current Wordle word list and write it to a text file."""

    # Get the source of the Wordle homepage and parse with BeautifulSoup.
    response = requests.get(WORDLE_URL + "index.html")
    soup = BeautifulSoup(response.text, "html.parser")

    # Collect script src attributes from the page (may be relative or absolute)
    script_srcs = [tag.get("src") for tag in soup.select("script[src]")]

    # Try to find and download the script that contains the word list. The
    # NYT builds include a JS file that contains a large array of 5-letter
    # words; match that array with a regex. We'll try each script src until a
    # match is found.
    wordlist = None
    best_match_info = None

    # Regex to find arrays of quoted 5-letter lowercase words inside brackets.
    array_re = re.compile(r"\[(?:\"[a-z]{5}\"(?:,\"[a-z]{5}\")*)\]")

    for src in filter(None, script_srcs):
        script_url = urljoin(WORDLE_URL, src)
        try:
            resp = requests.get(script_url, timeout=10)
        except requests.RequestException:
            continue
        if resp.status_code != 200:
            continue

        matches = list(array_re.finditer(resp.text))
        if not matches:
            continue

        # Evaluate each match and pick the one with the most items
        for m in matches:
            inner = m.group(0)[1:-1]
            items = [it.strip() for it in inner.split(",") if it.strip()]
            # verify all are quoted 5-letter lowercase words
            valid = all(re.fullmatch(r'"[a-z]{5}"', it) for it in items)
            if not valid:
                continue
            count = len(items)
            if not best_match_info or count > best_match_info[0]:
                best_match_info = (count, script_url, items)

    if not best_match_info:
        print("Could not find the Wordle word list in the page scripts. Try again later.")
        return

    count, matched_script_url, items = best_match_info
    # Remove surrounding quotes
    wordlist = [it[1:-1] for it in items]
    print(f"Found candidate word list with {count} entries in {matched_script_url}")

    # Write the word list to a text file.
    with open(FILENAME, "w", encoding="utf-8", newline="\n") as fhandle:
        for word in wordlist:
            fhandle.write(f"{word}\n")
    print(f"Current list of {len(wordlist)} words written to {FILENAME}")


if __name__ == "__main__":
    main()