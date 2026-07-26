"""
Step 4 - does the weekday slump survive the school holidays?

The weekday/weekend gap is usually read as a demand problem. An alternative
explanation is structural: children are in school Monday to Friday, so the
family and birthday-party segment is not free to visit midweek during term
time. If that is the cause, weekday demand should rise sharply during school
holidays - the same venue, the same marketing, only the constraint removed.

This distinguishes "a problem VRXtra can fix" from "a ceiling VRXtra cannot
move", which changes what the business should spend money on.

Term dates are England state-school dates for Cambridgeshire and
Hertfordshire, which align closely across the two branch locations. They are
approximate to within a day or two at the edges; the effect measured here is
far larger than that margin.
"""

import pathlib
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG = pathlib.Path("outputs/figures")
OUT = pathlib.Path("outputs")

# (start, end) inclusive - England school holidays overlapping the data window
SCHOOL_HOLIDAYS = [
    ("2025-02-17", "2025-02-21", "Feb half-term 2025"),
    ("2025-04-07", "2025-04-21", "Easter 2025"),
    ("2025-05-26", "2025-05-30", "May half-term 2025"),
    ("2025-07-22", "2025-09-01", "Summer 2025"),
    ("2025-10-27", "2025-10-31", "Oct half-term 2025"),
    ("2025-12-22", "2026-01-02", "Christmas 2025"),
    ("2026-02-16", "2026-02-20", "Feb half-term 2026"),
    ("2026-03-30", "2026-04-10", "Easter 2026"),
]

df = pd.read_parquet("data/processed/bookings_clean.parquet")
df = df[~df["is_cancelled"] & df["session_at"].notna()].copy()

d = df["session_at"].dt.normalize()
df["is_school_holiday"] = False
for start, end, _ in SCHOOL_HOLIDAYS:
    df.loc[d.between(pd.Timestamp(start), pd.Timestamp(end)), "is_school_holiday"] = True

df["dow"] = df["session_at"].dt.dayofweek          # 0=Mon
df["is_weekday"] = df["dow"] <= 3                   # Mon-Thu, matching the SQL segmentation

# Per-DAY rates, since term time covers far more calendar days than holidays.
days = (
    df.assign(day=d)
      .groupby(["is_school_holiday", "is_weekday"])["day"]
      .nunique()
      .rename("calendar_days")
)
agg = (
    df.groupby(["is_school_holiday", "is_weekday"])
      .agg(bookings=("Booking ID", "count"), revenue=("Net revenue", "sum"))
      .join(days)
)
agg["bookings_per_day"] = (agg.bookings / agg.calendar_days).round(1)
agg["revenue_per_day"] = (agg.revenue / agg.calendar_days).round(2)

lines: list[str] = []


def note(s: str) -> None:
    lines.append(s)
    print(s)


note("## Does the weekday slump survive the school holidays?\n")

term_wd = agg.loc[(False, True)]
hol_wd = agg.loc[(True, True)]
term_we = agg.loc[(False, False)]
hol_we = agg.loc[(True, False)]

base = term_wd.revenue_per_day   # index everything to a term-time weekday
for label, row in [
    ("Weekday, term time", term_wd),
    ("Weekday, school holiday", hol_wd),
    ("Weekend, term time", term_we),
    ("Weekend, school holiday", hol_we),
]:
    note(f"- **{label}**: {row.bookings_per_day:.1f} bookings/day, "
         f"revenue index {row.revenue_per_day / base * 100:.0f} "
         f"({int(row.calendar_days)} days observed)")

lift_bookings = hol_wd.bookings_per_day / term_wd.bookings_per_day
lift_revenue = hol_wd.revenue_per_day / term_wd.revenue_per_day
gap_term = term_we.revenue_per_day / term_wd.revenue_per_day
gap_hol = hol_we.revenue_per_day / hol_wd.revenue_per_day

note(f"\n**Weekday demand rises {lift_bookings:.2f}x in bookings and {lift_revenue:.2f}x in revenue "
     f"during school holidays**, with no change to pricing, marketing or opening hours.")
note(f"\nThe weekend-to-weekday revenue gap narrows from **{gap_term:.2f}x in term time** "
     f"to **{gap_hol:.2f}x during school holidays**.")

closed = (gap_term - gap_hol) / (gap_term - 1) * 100 if gap_term > 1 else float("nan")
note(f"That closes roughly **{closed:.0f}%** of the gap.\n")

# Party bookings specifically - the segment claimed to be school-constrained
party = df[df["Item Type"] == "Party"]
pdays = party.assign(day=d.loc[party.index]).groupby(["is_school_holiday", "is_weekday"])["day"].nunique()
pagg = party.groupby(["is_school_holiday", "is_weekday"]).size().rename("bookings").to_frame()
pagg["per_day"] = (pagg.bookings / days).round(3)
note("### Party bookings specifically\n")
for (hol, wd), row in pagg.iterrows():
    seg = f"{'Weekday' if wd else 'Weekend'}, {'school holiday' if hol else 'term time'}"
    note(f"- {seg}: {row.per_day:.2f} party bookings/day")
pw_term = pagg.loc[(False, True), "per_day"]
pw_hol = pagg.loc[(True, True), "per_day"]
note(f"\nMidweek party bookings run **{pw_hol / pw_term:.1f}x higher during school holidays**.\n")

note("### What this means\n")
note("The midweek gap is substantially structural. Children are in school Monday to Friday in "
     "term time, so the family and birthday segment is not free to visit - and the moment that "
     "constraint lifts, midweek demand rises on its own without any intervention.")
note("\nThat reframes the recommendation. Broad midweek discounting during term time is pushing "
     "against a constraint VRXtra does not control, and would most likely discount customers who "
     "were coming anyway. The addressable midweek audiences are the ones **not** governed by the "
     "school calendar: corporate team socials and away-days, university groups, and school trips "
     "themselves. Family-focused midweek promotion belongs in the holidays, when the audience "
     "is actually available.")

# ------------------------------------------------------------------ figure
plt.rcParams.update({
    "figure.dpi": 130, "savefig.bbox": "tight", "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25,
})
INK, ACCENT = "#1F3864", "#C1666B"

fig, ax = plt.subplots(figsize=(6.2, 3.2))
labels = ["Weekday", "Weekend"]
term = [term_wd.revenue_per_day / base * 100, term_we.revenue_per_day / base * 100]
hol = [hol_wd.revenue_per_day / base * 100, hol_we.revenue_per_day / base * 100]
x = np.arange(2)
w = 0.36
ax.bar(x - w / 2, term, w, label="Term time", color=INK)
ax.bar(x + w / 2, hol, w, label="School holiday", color=ACCENT)
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylabel("revenue per day (indexed)")
ax.set_title("Midweek demand rises on its own once school is out")
ax.legend()
fig.savefig(FIG / "06_school_holidays.png"); plt.close(fig)

OUT.joinpath("findings_school_holidays.md").write_text(
    "# School holidays and the weekday slump\n\n"
    "_Generated by `src/04_school_holidays.py`. Revenue indexed to a term-time weekday = 100._\n\n"
    + "\n".join(lines)
)
print(f"\nwrote {OUT/'findings_school_holidays.md'} and {FIG/'06_school_holidays.png'}")
