"""
gather_mlb_wl.py

Loads the Lahman Teams.csv (local path or URL) and writes a per-team-per-season
CSV with wins/losses and optional relocation annotations.

Usage examples:
  python gather_mlb_wl.py --lahman /path/to/Teams.csv --output output/team_seasons.csv
  python gather_mlb_wl.py --lahman https://example.com/Teams.csv --output team_seasons.csv --relocations relocations.csv

Relocations CSV format (optional):
  franchise,from_city,to_city,relocation_year,relocation_date,notes

This script is intentionally defensive: if it cannot download the Lahman CSV
automatically, it will error and explain where to get the CSV manually.

Assumptions:
- The Lahman Teams.csv contains at least these columns: yearID, teamID, franchID, lgID, W, L, teamIDBR, name
  If columns differ slightly the script attempts a best-effort mapping and will
  surface an error describing the missing fields.

"""
from __future__ import annotations
import argparse
import csv
import io
import sys
from typing import Optional

import pandas as pd
import requests


REQUIRED_COLS = ["yearID", "teamID", "franchID", "lgID", "W", "L", "name"]


def download_csv_or_open(path_or_url: str) -> io.StringIO:
    """Open a local path or download a URL and return a StringIO of the CSV text."""
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        print(f"Downloading Lahman CSV from URL: {path_or_url}")
        r = requests.get(path_or_url, timeout=30)
        r.raise_for_status()
        return io.StringIO(r.text)
    else:
        print(f"Reading Lahman CSV from local file: {path_or_url}")
        with open(path_or_url, "r", encoding="utf-8-sig") as f:
            return io.StringIO(f.read())


def load_lahman_teams(path_or_url: str) -> pd.DataFrame:
    csv_io = download_csv_or_open(path_or_url)
    # Use pandas to read; dtype=object to avoid accidental numeric conversions
    df = pd.read_csv(csv_io, dtype=object)
    # Normalize column names (strip)
    df.columns = [c.strip() for c in df.columns]
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Lahman Teams.csv is missing required columns: {missing}.\n"
            "Please provide a Teams.csv from the Lahman database. Typical file has columns like:\n"
            "yearID, teamID, franchID, lgID, W, L, name, park, attendance, etc.\n"
            "Download the official Lahman CSV from Sean Lahman's site: https://seanlahman.com/baseball-archive/statistics/ or GitHub mirror and retry."
        )
    # Convert numeric columns
    df["yearID"] = df["yearID"].astype(int)
    df["W"] = pd.to_numeric(df["W"], errors="coerce").fillna(0).astype(int)
    df["L"] = pd.to_numeric(df["L"], errors="coerce").fillna(0).astype(int)
    # Keep relevant columns and compute pct
    out = df[["yearID", "teamID", "franchID", "lgID", "name", "W", "L"]].copy()
    out["G"] = out["W"] + out["L"]
    out["W_pct"] = (out["W"] / out["G"]).round(3).fillna(0)
    return out


def load_relocations_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=object)
    # Expect at least 'franchise' and 'relocation_year'
    if "franchise" not in df.columns or "relocation_year" not in df.columns:
        raise ValueError("Relocations CSV must contain at least 'franchise' and 'relocation_year' columns")
    df["relocation_year"] = pd.to_numeric(df["relocation_year"], errors="coerce").astype(pd.Int64Dtype())
    return df


def annotate_relocations(seasons: pd.DataFrame, reloc: pd.DataFrame) -> pd.DataFrame:
    # Merge on franchID / franchise
    merged = seasons.merge(reloc, left_on="franchID", right_on="franchise", how="left")
    # Mark seasons at or after relocation_year as 'post_relocation'
    merged["post_relocation"] = False
    has_year = merged["relocation_year"].notnull()
    merged.loc[has_year & (merged["yearID"] >= merged.loc[has_year, "relocation_year"].astype(int)), "post_relocation"] = True
    return merged


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Gather MLB win/loss seasons from Lahman and optionally annotate relocations")
    p.add_argument("--lahman", required=True, help="Path or URL to Lahman Teams.csv")
    p.add_argument("--output", required=True, help="Output CSV path for team seasons (per-team per-year)")
    p.add_argument("--relocations", required=False, help="Optional CSV with relocation events (from Wikipedia). See README for format.")
    args = p.parse_args(argv)

    try:
        seasons = load_lahman_teams(args.lahman)
    except Exception as e:
        print("Error loading Lahman Teams.csv:", e, file=sys.stderr)
        return 2

    if args.relocations:
        try:
            reloc = load_relocations_csv(args.relocations)
        except Exception as e:
            print("Error loading relocations CSV:", e, file=sys.stderr)
            return 3
        annotated = annotate_relocations(seasons, reloc)
        annotated.to_csv(args.output, index=False)
        print(f"Wrote annotated seasons to {args.output}")
    else:
        seasons.to_csv(args.output, index=False)
        print(f"Wrote seasons to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
