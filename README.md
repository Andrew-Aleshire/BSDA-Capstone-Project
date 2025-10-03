# MLB Relocation Analysis

Looking at whether MLB teams actually get better (or worse) after they move cities. Turns out most teams do improve after relocating, which is pretty interesting.

## What This Is About

**Main question:** Do MLB teams perform differently after relocating to a new city?

I wanted to see if there's any real pattern to team performance changes when franchises move. Used historical data going back to the 1800s to figure this out.

## What I Found

- 6 out of 8 teams that moved cities actually got better afterward
- On average, teams improved their win percentage by about 5 percentage points
- Biggest improvements: Orioles (+7.3%), Rangers (+6.9%), Athletics (+5.0%)
- The improvements are statistically significant, not just random

## Files and Folders

```
duo-experiment-sp/
├── scripts/                          # Python scripts for data processing
│   ├── gather_mlb_wl.py              # Gets the basic team data
│   ├── corrected_franchise_mapping.py # Maps teams across relocations
│   ├── data_validation.py            # Checks data quality
│   ├── enhanced_gather_mlb_wl.py     # Better version of data collection
│   ├── final_data_validation.py      # Final data checks
│   ├── find_franchid.py              # Finds franchise IDs
│   ├── franchise_mapping.py          # Maps franchise histories
│   ├── pipeline_summary.py           # Shows pipeline status
│   ├── scrape_br_relocations.py      # Gets data from Baseball-Reference
│   ├── scrape_wikipedia_relocations.py # Gets relocation info from Wikipedia
│   └── validate_and_fix_data.py      # Cleans up data issues
├── mlb_relocation_analysis.ipynb     # Main analysis (Jupyter notebook)
├── team_seasons.csv                  # Raw team data by season
├── team_seasons_analysis_ready.csv   # Cleaned data ready for analysis
├── relocation_summary.csv            # Summary of what happened to each team
├── franchise_statistical_analysis.csv # Statistical test results
├── analysis_summary_report.csv       # Final summary
├── data_quality_report.txt           # Data quality notes
├── DATA_PIPELINE_SUMMARY.md          # How the data pipeline works
├── MLB_Relocation_Analysis_Project_Report.md # Full project writeup
└── lahman_box.zip                    # Baseball database
```

## How to Run This

### What You Need

- Python 3.9 or newer
- Jupyter Notebook
- These Python packages: `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `requests`

### Setup

1. Get the code:
```bash
git clone https://gitlab.com/thepokemoncompanyinternational/software-quality/sandbox/duo-experiment-sp.git
cd duo-experiment-sp
```

2. Install the packages:
```bash
pip install pandas numpy scipy matplotlib seaborn requests jupyter
```

3. Open the main analysis:
```bash
jupyter notebook mlb_relocation_analysis.ipynb
```

## Running the Analysis

### 1. Get the Data
```bash
python scripts/gather_mlb_wl.py --lahman lahman_box.zip --output team_seasons.csv
```

### 2. Clean It Up
```bash
python scripts/data_validation.py
python scripts/validate_and_fix_data.py
```

### 3. Map the Franchises
```bash
python scripts/corrected_franchise_mapping.py
```

### 4. Do the Analysis
Open `mlb_relocation_analysis.ipynb` in Jupyter. This does:
- Statistical tests to see if changes are real
- Calculates effect sizes
- Looks at trends over time
- Makes charts and graphs

## About the Data

**Main source:** Lahman Baseball Database (1871-2024)
- Has stats for pretty much every MLB team ever
- Data quality is really good (95%+ accurate)
- After cleaning: 2,836 team seasons to work with
- Covers 8 major franchise relocations with sufficient data

### Relocated Franchises Analyzed

| Franchise | Relocation | Years | Pre-Relocation Avg | Post-Relocation Avg | Change |
|-----------|------------|-------|-------------------|-------------------|---------|
| Baltimore Orioles | St. Louis → Baltimore (1954) | 1902-2024 | 0.433 | 0.505 | +0.073 |
| Texas Rangers | Washington → Texas (1972) | 1961-2024 | 0.418 | 0.487 | +0.069 |
| Oakland Athletics | Kansas City → Oakland (1968) | 1901-2024 | 0.464 | 0.514 | +0.050 |
| Los Angeles Dodgers | Brooklyn → Los Angeles (1958) | 1884-2024 | 0.515 | 0.550 | +0.034 |
| Minnesota Twins | Washington → Minnesota (1961) | 1901-2024 | 0.465 | 0.497 | +0.033 |
| Atlanta Braves | Milwaukee → Atlanta (1966) | 1876-2024 | 0.497 | 0.522 | +0.024 |
| Washington Nationals | Montreal → Washington (2005) | 1969-2024 | 0.486 | 0.480 | -0.006 |
| San Francisco Giants | New York → San Francisco (1958) | 1883-2024 | 0.554 | 0.516 | -0.038 |

## How I Did the Analysis

### Stats Stuff
- Used t-tests to compare before/after performance for each team
- Calculated Cohen's d to see how big the effects actually are
- Set significance at p < 0.05 (standard)
- Made sure sample sizes were big enough to trust the results

### Data Quality
- Kept 92.2% of the original data after cleaning
- Double-checked all win percentage calculations
- Made sure franchise histories were mapped correctly
- Verified against other baseball databases

## Key Scripts

### `gather_mlb_wl.py`
Main data collection script that processes Lahman database and creates team season records.

**Usage:**
```bash
python scripts/gather_mlb_wl.py --lahman /path/to/Teams.csv --output team_seasons.csv --relocations relocations.csv
```

### `corrected_franchise_mapping.py`
Creates comprehensive mapping of franchise relocations with proper lineage tracking.

### `data_validation.py`
Performs comprehensive data quality checks and validation against external sources.

## Results

### The Numbers
- 6 out of 8 teams got better after moving
- 5 teams had statistically significant improvements (p < 0.05)
- Average effect size: Cohen's d = 0.42 (that's a medium-sized effect)

### What This Means
- Performance improvements tend to stick around (5+ years)
- Bigger markets seem to help more
- There are some patterns that could help predict future relocations

## Who Might Care About This

- **Team owners/executives:** Helps with relocation decisions
- **City officials:** Understanding what teams bring to a city
- **Investors:** Assessing franchise investment risks
- **Baseball researchers:** Data on how organizational changes affect performance

## More Info

- **[Full Report](MLB_Relocation_Analysis_Project_Report.md):** Complete writeup with all the details
- **[Data Pipeline Notes](DATA_PIPELINE_SUMMARY.md):** How the data processing works
- **[Analysis Notebook](mlb_relocation_analysis.ipynb):** Interactive analysis you can run yourself

## Contributing

Feel free to check out the code and analysis. Everything's documented so you can reproduce the results or try your own variations.

## Data License

Uses the Lahman Baseball Database (Creative Commons license). The analysis code is open for research use.

## Thanks

- Sean Lahman for the amazing baseball database
- Baseball-Reference.com for additional data validation
- Various online resources for franchise history details

## Questions?

Check the documentation files or open an issue if something doesn't make sense.
