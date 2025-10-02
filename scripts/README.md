Gather MLB W-L data (Lahman + Baseball-Reference) and relocations

This small utility helps the user extract per-team-per-season win/loss records from
the Lahman Baseball Database `Teams.csv` and optionally annotate seasons
relative to franchise relocations.

Where to get the data
- Lahman Teams.csv: The canonical source is Sean Lahman's site (https://seanlahman.com/baseball-archive/statistics/). Download the latest CSV package and extract `Teams.csv`.
- Baseball-Reference: Useful for cross-checking and additional team identifiers. See https://www.baseball-reference.com/teams/ for team pages.
- Wikipedia: Use team pages or lists of relocations (for example, individual team pages like "Montreal Expos" or "Washington Nationals", or lists such as "List of defunct and relocated Major League Baseball teams") to gather relocation dates and cities. Create a CSV with columns: franchise,from_city,to_city,relocation_year,relocation_date,notes

Usage
1. Install dependencies (recommended inside a virtualenv):
   pip install -r requirements.txt

2. Run the script pointing at your local `Teams.csv`:
   python gather_mlb_wl.py --lahman /path/to/Teams.csv --output ./team_seasons.csv

3. (Optional) Provide a relocations CSV to annotate post-relocation seasons:
   python gather_mlb_wl.py --lahman Teams.csv --output annotated.csv --relocations relocations.csv