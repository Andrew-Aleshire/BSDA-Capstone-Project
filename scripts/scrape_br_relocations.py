"""
scrape_br_relocations.py

Scrapes the Baseball-Reference Bullpen Relocation page and writes a cleaned
relocations CSV with columns: franchise,from_city,to_city,relocation_year,relocation_date,notes

Usage:
  python scrape_br_relocations.py --output relocations_br.csv

"""
from __future__ import annotations
import argparse
import csv
import re
from typing import List

import requests
from bs4 import BeautifulSoup


URL = "https://www.baseball-reference.com/bullpen/Relocation"


def fetch(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}
    r = requests.get(url, timeout=30, headers=headers)
    r.raise_for_status()
    return r.text


def parse_br_relocation_text(text: str) -> List[dict]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    rows: List[dict] = []

    team_pat = re.compile(r"^\[?(?P<team>[^\]]+)\]?\s*:\s*\[?(?P<year>\d{4})\]?\s*-\s*present", re.I)
    relocated_pat = re.compile(r"Relocated from:\s*\[?(?P<city>[^\]]+)\]?\s*\[?(?P<start>\d{4})\]?(?:\s*-\s*\[?(?P<end>\d{4})\]?)?", re.I)

    i = 0
    while i < len(lines):
        m = team_pat.match(lines[i])
        if m:
            team = m.group('team').strip()
            team_start = int(m.group('year'))
            # look ahead for Relocated from lines
            j = i + 1
            while j < len(lines):
                # stop if next team header
                if team_pat.match(lines[j]):
                    break
                rm = relocated_pat.search(lines[j])
                if rm:
                    city = rm.group('city').strip()
                    # relocation year: use team_start as the year the franchise began in new city
                    relocation_year = team_start
                    notes = lines[j]
                    rows.append({
                        'franchise': team,
                        'from_city': city,
                        'to_city': team,
                        'relocation_year': relocation_year,
                        'relocation_date': '',
                        'notes': notes,
                        'raw': lines[j]
                    })
                j += 1
            i = j
        else:
            i += 1

    return rows


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--output', default='relocations_br.csv')
    args = p.parse_args(argv)

    print(f"Fetching {URL}")
    html = fetch(URL)
    soup = BeautifulSoup(html, 'lxml')
    content = soup.find('div', class_='mw-parser-output')
    if content is None:
        text = soup.get_text('\n')
    else:
        text = content.get_text('\n')

    rows = parse_br_relocation_text(text)
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['franchise', 'from_city', 'to_city', 'relocation_year', 'relocation_date', 'notes', 'raw']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {len(rows)} relocation rows to {args.output}")


if __name__ == '__main__':
    main()
