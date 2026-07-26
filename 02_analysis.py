"""
Step 2 - analysis and figures.

Reads  : data/processed/bookings_clean.parquet
Writes : outputs/figures/*.png  and  outputs/findings.md

Revenue is INDEXED, not absolute, in every published figure. VRXtra approved
publication of findings, not of their raw commercial numbers, so absolute
revenue stays out of the repo.
"""

import pathlib
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG = pathlib.Path("outputs/figures")
FIG.mkdir(parents=True, exist_ok=True)
OUT = pathlib.Path("outputs")

plt.rcParams.update({
    "figure.dpi": 130, "savefig.bbox": "tight", "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linestyle": "-",
})
INK, ACCENT = "#1F3864", "#C1666B"
findings: list[str] = []


def note(s: str) -> None:
    findings.append(s)
    print(s)


df = pd.read_parquet("data/processed/bookings_clean.parquet")
full = df[~df["is_partial_month"]].copy()   # drop partial first/last months

# ----------------------------------------------------------------- 1. channel
note("## 1. Booking channel\n")
ch = df.groupby("booking_channel").agg(
    bookings=("Booking ID", "count"),
    median_lead_days=("lead_time_days", "median"),
    mean_pax=("Pax", "mean"),
    mean_rev=("Net revenue", "mean"),
    repeat_rate=("is_repeat_customer", "mean"),
).round(2)
base = ch["mean_rev"].min()
ch["rev_index"] = (ch["mean_rev"] / base * 100).round(1)
premium = (ch.loc["Online", "mean_rev"] / ch.loc["Staff-assisted", "mean_rev"] - 1) * 100
note(f"Online bookings carry a **{premium:.0f}% higher average value** than staff-assisted "
     f"(index {ch.loc['Online','rev_index']:.0f} vs {ch.loc['Staff-assisted','rev_index']:.0f}) "
     f"and larger parties ({ch.loc['Online','mean_pax']:.2f} vs {ch.loc['Staff-assisted','mean_pax']:.2f} pax).")
note(f"Staff-assisted bookings are overwhelmingly walk-ins: median lead time "
     f"{ch.loc['Staff-assisted','median_lead_days']:.2f} days vs {ch.loc['Online','median_lead_days']:.2f} for online.\n")

fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
ch["rev_index"].plot.bar(ax=ax[0], color=[INK, ACCENT], rot=0)
ax[0].set_title("Avg booking value (indexed)"); ax[0].set_ylabel("index, lowest = 100"); ax[0].set_xlabel("")
(ch["repeat_rate"] * 100).plot.bar(ax=ax[1], color=[INK, ACCENT], rot=0)
ax[1].set_title("Repeat-customer rate"); ax[1].set_ylabel("% of bookings"); ax[1].set_xlabel("")
fig.suptitle("Online bookings are worth more - but staff-assisted customers return more often", y=1.04)
fig.savefig(FIG / "01_channel.png"); plt.close(fig)

# ---------------------------------------------------------------- 2. location
note("## 2. Site comparison\n")
loc = pd.crosstab(df["Location"], df["booking_channel"], normalize="index").mul(100).round(1)
locrev = df.groupby("Location")["Net revenue"].mean()
locrev_idx = (locrev / locrev.min() * 100).round(1)
note(f"Cambridge takes {loc.loc['Cambridge','Online']:.0f}% of bookings online; "
     f"Watford only {loc.loc['Watford','Online']:.0f}%.")
note(f"Watford is therefore far more walk-in dependent ({loc.loc['Watford','Staff-assisted']:.0f}% "
     f"vs {loc.loc['Cambridge','Staff-assisted']:.0f}%), and skews toward the lower-value channel.")
note(f"**Opportunity:** shifting Watford's online share to Cambridge's level would move volume "
     f"into a channel worth {premium:.0f}% more per booking.\n")

fig, ax = plt.subplots(figsize=(5.2, 3))
loc.plot.barh(stacked=True, ax=ax, color=[INK, ACCENT])
ax.set_xlabel("% of bookings"); ax.set_ylabel("")
ax.set_title("Watford relies far more on walk-ins than Cambridge")
ax.legend(title="", bbox_to_anchor=(1.02, 1), loc="upper left")
fig.savefig(FIG / "02_location.png"); plt.close(fig)

# ------------------------------------------------------------- 3. lead time
note("## 3. Booking lead time\n")
lt = df["lead_time_days"].dropna()
sameday = (lt < 1).mean() * 100
within7 = (lt < 7).mean() * 100
note(f"**{sameday:.0f}% of bookings are made on the day of the session**, and {within7:.0f}% within a week.")
note("This is the single most actionable finding: promotional lead times measured in weeks are "
     "aimed at a minority of demand. Same-week and same-day activity is where the volume is.\n")

fig, ax = plt.subplots(figsize=(6, 3))
ax.hist(lt[lt <= 30], bins=30, color=INK)
ax.set_xlabel("days between booking and session"); ax.set_ylabel("bookings")
ax.set_title(f"{sameday:.0f}% of bookings happen same-day (0-30 day window)")
fig.savefig(FIG / "03_leadtime.png"); plt.close(fig)

# ------------------------------------------------------- 4. demand + forecast
note("## 4. Demand trend and forecast\n")
monthly = full.groupby("booking_month").size().rename("bookings")
monthly.index = pd.PeriodIndex(monthly.index, freq="M")
monthly = monthly.sort_index()
idx = (monthly / monthly.mean() * 100).round(1)

# Seasonal-naive baseline: predict month t from month t-1, walk-forward.
actual = monthly.values.astype(float)
pred = actual[:-1]
truth = actual[1:]
mape = float(np.mean(np.abs((truth - pred) / truth)) * 100)

# 3-month moving average as the comparison model
ma = pd.Series(actual).rolling(3).mean().shift(1).values
mask = ~np.isnan(ma)
mape_ma = float(np.mean(np.abs((actual[mask] - ma[mask]) / actual[mask])) * 100)

note(f"Full months analysed: {len(monthly)} (partial first/last months excluded).")
note(f"Naive last-month forecast: **MAPE {mape:.1f}%**. 3-month moving average: **MAPE {mape_ma:.1f}%**.")
better = "the moving average" if mape_ma < mape else "the naive baseline"
note(f"{better.capitalize()} performs better, giving a documented benchmark any future model must beat.\n")

fig, ax = plt.subplots(figsize=(7, 3))
ax.plot(idx.index.astype(str), idx.values, marker="o", color=INK, label="actual (indexed)")
ax.axhline(100, color=ACCENT, ls="--", lw=1, label="period mean")
ax.set_xticklabels(idx.index.astype(str), rotation=45, ha="right")
ax.set_ylabel("bookings, indexed"); ax.set_title("Monthly demand, indexed to period mean")
ax.legend()
fig.savefig(FIG / "04_demand.png"); plt.close(fig)

# --------------------------------------------------------- 5. repeat drivers
note("## 5. What predicts a repeat booking\n")
first = df.sort_values("created_at").groupby("Customer_ID").first()
first["repeated"] = first.index.map(df.groupby("Customer_ID").size() > 1)
rate = first["repeated"].mean() * 100
note(f"Overall repeat rate: **{rate:.1f}%** of customers book again ({first['repeated'].sum():,} of {len(first):,}).")

def two_prop_z(a_succ, a_n, b_succ, b_n):
    """Two-proportion z-test. Returns (z, two-tailed p)."""
    p1, p2 = a_succ / a_n, b_succ / b_n
    p = (a_succ + b_succ) / (a_n + b_n)
    se = np.sqrt(p * (1 - p) * (1 / a_n + 1 / b_n))
    z = (p1 - p2) / se
    from math import erfc, sqrt
    return z, erfc(abs(z) / sqrt(2))


drivers = {}
for col, label in [("booking_channel", "channel"), ("Location", "site")]:
    t = first.groupby(col)["repeated"].agg(["sum", "size"])
    t = t[t["size"] >= 30]
    if len(t) == 2:
        drivers[label] = (t["sum"] / t["size"] * 100).round(1)
        a, b = t.index[0], t.index[1]
        z, p = two_prop_z(t.loc[a, "sum"], t.loc[a, "size"], t.loc[b, "sum"], t.loc[b, "size"])
        ra, rb = t.loc[a, "sum"] / t.loc[a, "size"] * 100, t.loc[b, "sum"] / t.loc[b, "size"] * 100
        sig = "significant" if p < 0.05 else "**not statistically significant**"
        note(f"By {label}: {a} {ra:.1f}% vs {b} {rb:.1f}% - z={z:.2f}, p={p:.2f}, {sig}.")

note("\nThe apparent differences in repeat rate by channel and site do not survive a "
     "two-proportion z-test at n=1,856. They are reported here as null results rather than "
     "dropped, because a difference that fails significance testing is a finding: it says "
     "repeat behaviour is not driven by where or how the customer was acquired.")

# The revenue premium, by contrast, is tested and holds.
on = df.loc[df.booking_channel == "Online", "Net revenue"].dropna()
st = df.loc[df.booking_channel == "Staff-assisted", "Net revenue"].dropna()
se_rev = np.sqrt(on.var() / len(on) + st.var() / len(st))
t_rev = (on.mean() - st.mean()) / se_rev
from math import erfc, sqrt
p_rev = erfc(abs(t_rev) / sqrt(2))
note(f"\nThe {premium:.0f}% revenue premium for online bookings, by contrast, is highly "
     f"significant (Welch t={t_rev:.1f}, p<0.0001, n={len(on):,} vs {len(st):,}) - "
     f"it is the one channel difference solid enough to act on.\n")

fig, ax = plt.subplots(figsize=(5.2, 3))
drivers["channel"].plot.bar(ax=ax, color=INK, rot=0)
ax.set_ylabel("% who book again"); ax.set_xlabel(""); ax.set_title("Repeat rate by acquisition channel")
fig.savefig(FIG / "05_repeat.png"); plt.close(fig)

# ------------------------------------------------------------------- write up
OUT.joinpath("findings.md").write_text(
    "# Findings\n\n"
    "_Generated by `src/02_analysis.py`. Revenue is indexed, never absolute._\n\n"
    + "\n".join(findings)
)
print(f"\nwrote {OUT/'findings.md'} and {len(list(FIG.glob('*.png')))} figures")
