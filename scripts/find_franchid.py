import sys
import os
import pandas as pd

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    default_csv = os.path.join(repo_root, 'team_seasons.csv')
    csv_path = sys.argv[1] if len(sys.argv) > 1 else default_csv

    if not os.path.exists(csv_path):
        print(f"ERROR: input CSV not found: {csv_path}")
        sys.exit(2)

    df = pd.read_csv(csv_path, dtype=str)

    required_cols = {'franchID', 'name'}
    if not required_cols.issubset(df.columns):
        print(f"ERROR: CSV missing required columns: {required_cols - set(df.columns)}")
        sys.exit(3)

    lookup = ['Dodgers','Giants','Athletics','Braves','Twins','Rangers','Brewers','Nationals','Expos','Orioles']
    pattern = '|'.join(lookup)

    matches = df[df['name'].str.contains(pattern, case=False, na=False)][['franchID','name']].drop_duplicates().sort_values('name')

    out_path = os.path.join(os.path.dirname(__file__), 'franchid_pairs.csv')
    matches.to_csv(out_path, index=False)

    print(f"Wrote {out_path}\n")
    print(matches.to_csv(index=False))

if __name__ == '__main__':
    main()
