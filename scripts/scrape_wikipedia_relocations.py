"""
scrape_wikipedia_relocations.py

Fetches relevant Wikipedia pages to build a relocations CSV with columns:
  franchise,from_city,to_city,relocation_year,relocation_date,notes

Notes:
- This script scrapes publicly available Wikipedia pages and is intended as a
  convenience tool to collect relocation dates. Wikipedia content may change
  and should be verified before using for publication.

Usage:
  python scrape_wikipedia_relocations.py --output relocations.csv

"""
from __future__ import annotations
import argparse
import csv
import re
from typing import List

import requests
from bs4 import BeautifulSoup


WIKI_PAGES = [
    "https://en.wikipedia.org/wiki/List_of_defunct_and_relocated_Major_League_Baseball_teams",
]


def parse_list_page(html: str) -> List[dict]:
    soup = BeautifulSoup(html, "lxml")
    rows = []
    # The page contains lists; we'll look for tables with team names and notes
    tables = soup.find_all("table")
    for t in tables:
        # Try to parse rows with links mentioning relocations
        for tr in t.find_all("tr"):
            tds = tr.find_all(["td", "th"])
            if not tds:
                continue
            text = " ".join(td.get_text(separator=" ") for td in tds)
            # crude heuristic: look for 'moved' or 'relocated' and a year
            if re.search(r"moved|relocat|relocated|became|transferred", text, re.I) and re.search(r"\b(18|19|20)\d{2}\b", text):
                rows.append({"raw": text.strip()})
    return rows


def fetch(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}
    r = requests.get(url, timeout=30, headers=headers)
    r.raise_for_status()
    return r.text


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="relocations.csv")
    args = p.parse_args(argv)

    found = []
    for url in WIKI_PAGES:
        print(f"Fetching {url}")
        try:
            html = fetch(url)
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            continue
        rows = parse_list_page(html)
        print(f"Found {len(rows)} potential relocation notes on {url}")
        found.extend(rows)

    # Write raw results for manual review
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["franchise", "from_city", "to_city", "relocation_year", "relocation_date", "notes", "raw"])
        writer.writeheader()
        for r in found:
            out = {"franchise": "", "from_city": "", "to_city": "", "relocation_year": "", "relocation_date": "", "notes": "", "raw": r["raw"]}
            writer.writerow(out)

    print(f"Wrote {len(found)} raw relocation rows to {args.output}. Review and fill 'franchise' and 'relocation_year' columns for annotation.")


if __name__ == "__main__":
    main()
