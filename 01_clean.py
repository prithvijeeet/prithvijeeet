"""
Step 1 - clean and pseudonymise the raw booking export.

Reads  : data/raw/VRXtra_Cleaned_Sorted-2.csv
Writes : data/processed/bookings_clean.parquet  (gitignored - never published)

What it does, and why:

1. PSEUDONYMISES `Created By`. The raw column contains 18 real staff names
   alongside "Online". Those are identifiable third parties who have not
   consented to publication, so every name is mapped to a stable Staff_NN
   token. The lookup is written to data/processed/ (gitignored) so the
   analysis stays reproducible locally without ever exposing a name.

2. Adds `booking_channel` (Online vs Staff-assisted). This is the publishable
   view of the same signal and is more analytically useful than per-person
   comparison.

3. Fixes known category dirt: "Mealdeal" -> "Meal Deal".

4. Parses `Created At` (when the booking was made) and `Availability` (when
   the session runs), then derives `lead_time_days` between them.

5. Flags partial months. The export starts 11 Jan 2025 and ends 14 Apr 2026,
   so the first and last months are incomplete. Any month-on-month trend that
   ignores this shows a fake collapse at both ends.
"""

import pathlib
import pandas as pd

RAW = pathlib.Path("data/raw/VRXtra_Cleaned_Sorted-2.csv")
OUT_DIR = pathlib.Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_availability(s: pd.Series) -> pd.Series:
    """`Availability` looks like '17/1/26 @ 12:40' - day-first, 2-digit year."""
    cleaned = s.astype(str).str.replace(" @ ", " ", regex=False).str.strip()
    return pd.to_datetime(cleaned, dayfirst=True, errors="coerce")


def main() -> None:
    df = pd.read_csv(RAW)
    n_in = len(df)

    # --- 1. pseudonymise staff -------------------------------------------
    staff = sorted([v for v in df["Created By"].dropna().unique() if v != "Online"])
    mapping = {name: f"Staff_{i:02d}" for i, name in enumerate(sorted(staff), start=1)}
    mapping["Online"] = "Online"
    df["created_by_id"] = df["Created By"].map(mapping)

    pd.DataFrame(
        {"original": list(mapping.keys()), "pseudonym": list(mapping.values())}
    ).to_csv(OUT_DIR / "staff_lookup.csv", index=False)
    df = df.drop(columns=["Created By"])

    # --- 2. publishable channel split ------------------------------------
    df["booking_channel"] = df["created_by_id"].apply(
        lambda v: "Online" if v == "Online" else "Staff-assisted"
    )

    # --- 3. category dirt -------------------------------------------------
    df["Item Type"] = df["Item Type"].replace({"Mealdeal": "Meal Deal"})

    # --- 4. dates and lead time ------------------------------------------
    df["created_at"] = pd.to_datetime(df["Created At"], errors="coerce")
    df["session_at"] = parse_availability(df["Availability"])
    df["lead_time_days"] = (df["session_at"] - df["created_at"]).dt.total_seconds() / 86400

    # Negative lead time = session logged before the booking record; treat as invalid.
    bad_lead = (df["lead_time_days"] < 0).sum()
    df.loc[df["lead_time_days"] < 0, "lead_time_days"] = pd.NA

    df["booking_month"] = df["created_at"].dt.to_period("M").astype(str)
    df["booking_dow"] = df["created_at"].dt.day_name()
    df["is_cancelled"] = df["Cancelled?"].eq("Cancelled")

    # --- 5. partial-month flag -------------------------------------------
    months = df["booking_month"]
    partial = {months.min(), months.max()}
    df["is_partial_month"] = months.isin(partial)

    # --- repeat-customer features ----------------------------------------
    counts = df["Customer_ID"].value_counts()
    df["customer_booking_count"] = df["Customer_ID"].map(counts)
    df["is_repeat_customer"] = df["customer_booking_count"] > 1
    df = df.sort_values("created_at")
    df["booking_seq"] = df.groupby("Customer_ID").cumcount() + 1

    df.to_parquet(OUT_DIR / "bookings_clean.parquet", index=False)

    print(f"rows in/out          : {n_in:,} / {len(df):,}")
    print(f"staff pseudonymised  : {len(staff)} names -> Staff_01..Staff_{len(staff):02d}")
    print(f"channel split        : {df['booking_channel'].value_counts().to_dict()}")
    print(f"invalid lead times   : {bad_lead} (set to NA)")
    print(f"lead time median     : {df['lead_time_days'].median():.1f} days")
    print(f"partial months       : {sorted(partial)}")
    print(f"repeat customers     : {df['is_repeat_customer'].sum():,} bookings from repeaters")
    print(f"\nwrote {OUT_DIR/'bookings_clean.parquet'} (gitignored)")


if __name__ == "__main__":
    main()
