"""
Step 0 - profile the raw booking export.

Run this first, before any analysis. It reports the schema, date coverage,
missingness and cardinality so the analysis can be built against what the
data actually contains rather than what we assume it contains.

It also FLAGS LIKELY PERSONAL DATA (names, emails, phones, addresses,
postcodes) so those columns can be dropped before anything is published.

Usage:
    python3 src/00_profile_data.py data/raw/<your-export>.csv
    python3 src/00_profile_data.py data/raw/<your-export>.xlsx
"""

import sys
import pathlib
import pandas as pd

PII_HINTS = [
    "name", "email", "mail", "phone", "mobile", "tel", "address",
    "postcode", "post_code", "zip", "dob", "birth", "card", "ip",
]


def load(path: pathlib.Path) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path, low_memory=False)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("usage: python3 src/00_profile_data.py <path-to-export>")

    path = pathlib.Path(sys.argv[1])
    if not path.exists():
        sys.exit(f"not found: {path}")

    df = load(path)
    print(f"\nfile:  {path.name}")
    print(f"rows:  {len(df):,}")
    print(f"cols:  {len(df.columns)}\n")

    print(f"{'column':<34} {'dtype':<12} {'nulls':>7} {'unique':>8}  example")
    print("-" * 100)
    for c in df.columns:
        s = df[c]
        null_pct = f"{s.isna().mean() * 100:.0f}%"
        example = s.dropna().iloc[0] if s.notna().any() else ""
        example = str(example)[:26]
        print(f"{c[:33]:<34} {str(s.dtype):<12} {null_pct:>7} {s.nunique():>8}  {example}")

    # Personal-data flags
    flagged = [c for c in df.columns if any(h in c.lower() for h in PII_HINTS)]
    if flagged:
        print("\n" + "!" * 76)
        print("LIKELY PERSONAL DATA - drop these before publishing anything:")
        for c in flagged:
            print(f"   - {c}")
        print("!" * 76)
    else:
        print("\nNo obvious personal-data column names detected.")
        print("Still eyeball free-text columns manually before publishing.")

    # Date coverage
    date_cols = [
        c for c in df.columns
        if "date" in c.lower() or "time" in c.lower() or "created" in c.lower()
    ]
    for c in date_cols:
        parsed = pd.to_datetime(df[c], errors="coerce")
        if parsed.notna().any():
            span_days = (parsed.max() - parsed.min()).days
            print(f"\ndate column '{c}': {parsed.min().date()} -> {parsed.max().date()} ({span_days} days)")

    # Candidate numeric measures
    nums = df.select_dtypes("number").columns.tolist()
    if nums:
        print(f"\nnumeric columns (candidate measures): {', '.join(nums[:12])}")

    print("\nnext: share this output and the analysis will be built against this schema.\n")


if __name__ == "__main__":
    main()
