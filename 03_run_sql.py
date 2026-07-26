"""
Step 3 - execute the SQL layer and publish indexed results.

Runs every query in sql/ against the cleaned data via DuckDB, then writes the
results to outputs/sql/ with ALL ABSOLUTE REVENUE CONVERTED TO AN INDEX.

Indexing rule (applied to every column whose name contains 'revenue'):
    index = revenue / mean_net_revenue_per_booking * 100
So 100 = the value of one average booking. Shape, ratios and comparisons are
all preserved; VRXtra's actual takings are not published.

Percentage and count columns pass through untouched - they reveal nothing
absolute.
"""

import pathlib
import duckdb
import pandas as pd

SQL = pathlib.Path("sql")
OUT = pathlib.Path("outputs/sql")
OUT.mkdir(parents=True, exist_ok=True)

con = duckdb.connect()
con.execute(SQL.joinpath("00_base_view.sql").read_text())

BASE = con.execute("SELECT AVG(net_revenue) FROM bookings").fetchone()[0]
print(f"index base: 100 = one average booking\n")


def index_revenue(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in out.columns:
        lc = c.lower()
        if "revenue" in lc and "pct" not in lc and "percentage" not in lc:
            if pd.api.types.is_numeric_dtype(out[c]):
                out[c] = (out[c] / BASE * 100).round(1)
                out = out.rename(columns={c: f"{c}_indexed"})
    return out


for f in sorted(SQL.glob("0[1-9]_*.sql")):
    df = con.execute(f.read_text()).df()
    idx = index_revenue(df)
    dest = OUT / f"{f.stem}.csv"
    idx.to_csv(dest, index=False)
    n_idx = sum("_indexed" in c for c in idx.columns)
    print(f"{f.name:38} {len(df):>5} rows  ->  {dest.name}  ({n_idx} revenue cols indexed)")

# ---------------------------------------------------------------- validation
print("\n--- reconciliation against the source system ---")
tot = con.execute("SELECT COUNT(*), ROUND(SUM(net_revenue),2) FROM bookings").fetchone()
print(f"bookings: {tot[0]:,}   net revenue: £{tot[1]:,.2f}")
print("expected: 2,135 bookings, £180,081.98  (cancelled bookings excluded)")
print("match:", "YES" if tot[0] == 2135 and abs(tot[1] - 180081.98) < 0.01 else "NO - investigate")
