# VRXtra Booking Analytics

**Management believed there was a weekday slump and a weekend rush. This analysis of 2,135 bookings across two UK VR venues tested whether that was true — and found the real cause was not the one assumed.**

I work at VRXtra as a VR Instructor. In a conversation about trading patterns, management described a weekday slump and a weekend rush as an accepted fact of the business. Nobody had tested it against the booking data, and 15 months of that data was sitting unused. I offered to check.

---

## The answer to the original question

**Yes — but it is not a slump, and it is not what management thought it was.**

Measured per day, rather than by lumping four weekdays against three weekend days:

| Per calendar day | Bookings | Revenue (indexed) | Revenue per booking |
|---|---|---|---|
| Weekday (Mon–Thu) | 3.27 | 100 | £66.27 |
| Weekend (Fri–Sun) | 7.83 | **334** | £92.35 |

The weekend does **3.3× a weekday's revenue per day**, and takes 76% of all revenue from 69% of bookings.

**But the diagnosis is more specific than "fewer people come midweek."** Splitting by what people book:

| | Midweek | Weekend | Gap |
|---|---|---|---|
| Individual bookings | 604 | 1,287 | 2.1× |
| **Party bookings** | **20** | **171** | **8.6×** |

Individuals still turn up midweek. **Group bookings almost completely disappear** — and because parties carry a far higher value, that single gap explains most of the £66 vs £92 difference in revenue per booking.

So the weekday slump is not a general footfall problem. But the obvious next move — "sell parties into midweek" — turns out to be wrong too, and the reason is the most interesting thing in this analysis.

### The gap is mostly structural, and the data proves it

If midweek is quiet because children are in school, then removing that constraint should lift midweek demand on its own. School holidays are exactly that natural experiment: same venue, same prices, same marketing, no children in school.

![School holidays](outputs/figures/06_school_holidays.png)

| Per calendar day | Term time | School holiday |
|---|---|---|
| Weekday revenue (indexed) | 100 | **283** |
| Weekend revenue (indexed) | 565 | 407 |

**Midweek demand rises 3.2× in bookings and 2.8× in revenue during school holidays, with no intervention at all.** The weekend-to-weekday gap collapses from **5.65× in term time to 1.44× in the holidays** — roughly **91% of the gap disappears** the moment school is out.

The midweek slump is therefore largely a **constraint VRXtra does not control**. Discounting midweek during term time pushes against the school calendar and would mostly discount customers who were coming anyway.

### And parties are a term-time weekend phenomenon

| Party bookings per day | Term time | School holiday |
|---|---|---|
| Weekend | **1.06** | 0.25 |
| Weekday | 0.10 | 0.11 |

Parties barely move midweek even when school is out (0.10 → 0.11), and weekend parties actually *fall* during holidays. That fits: a children's party needs the child's classmates, and classmates are only reliably assembled during term time. Holidays scatter them.

So the holiday midweek lift is driven by **families and individuals**, not parties — and no midweek offer will move the birthday segment, because the constraint is other people's school calendars.

**What that leaves as genuinely addressable:** audiences not governed by the school calendar — corporate team socials and away-days, university groups, and school trips themselves. Family-focused midweek promotion belongs in the holidays, when the audience is actually free.

One caveat on the segmentation: Friday sits between the two worlds (244 bookings across the period, against ~160 for a typical midweek day and 764 on Saturdays). Grouping it as "weekend" flatters the weekend average. Saturday and Sunday are the true peak.

---

## Further findings

### 1. Online bookings are worth 32% more than walk-ins — and it holds up statistically

Online bookings average a 32% higher net value than staff-assisted ones, with larger parties (3.35 vs 2.93 people). Tested with a Welch t-test: **t = 7.6, p < 0.0001** across 1,386 vs 760 bookings. This is not a sampling artefact.

![Channel comparison](outputs/figures/01_channel.png)

### 2. Watford is leaving money on the table

Cambridge takes **74%** of its bookings online. Watford takes **54%** — nearly half its volume walks in off the street, into the channel worth 32% less.

![Site comparison](outputs/figures/02_location.png)

**Recommendation:** shift Watford's channel mix toward Cambridge's. This is a marketing problem, not an operational one.

**But size it honestly.** I built a scenario model ([`outputs/Watford_Online_Shift_Model.xlsx`](outputs/Watford_Online_Shift_Model.xlsx)) to quantify it rather than leave it as a directional claim. Closing the *entire* 20-point gap is worth roughly **+2.3% annual revenue** at a 50% premium-realisation assumption — around +4.5% at an implausible 100%.

That is worth doing and cheap to attempt, but it is not transformative, and the model exists partly to stop the finding being oversold. Watford's site-specific premium is also **25.9%**, not the 32% all-sites figure — the smaller number is the right one for a Watford decision.

The model's central assumption is deliberately conservative: the premium is **observed, not proven causal**. Online bookings may be worth more because people planning ahead bring larger groups, not because the channel raises spend. Moving a walk-in online may capture none of that gap, which is why "premium realisation" is an explicit input defaulted to 50% rather than buried at 100%. Only a controlled test resolves it.

### 3. Over half of all bookings are made on the day

**53% of bookings happen same-day**, and 75% within a week. Median lead time for a walk-in is 15 minutes; for an online booking, 2 days.

![Lead time](outputs/figures/03_leadtime.png)

That looks like an argument for same-day promotion. It isn't — and this is the most important correction in the project.

Segmenting the same bookings by **revenue** rather than count reverses the conclusion:

| Booking horizon | Share of bookings | Revenue per booking | Share of revenue |
|---|---|---|---|
| Same-day | 46% | £53.60 | 29% |
| 2+ weeks ahead | 15% | **£166.67** | 29% |

**Advance planners generate the same revenue from a third of the volume — 3.1× more per booking.** In the weekend segment they are the single largest revenue block (33.4%).

Counting bookings says same-day dominates. Counting money says planners do. Marketing spend aimed at same-day demand is chasing the cheaper half of the business; the planners are where campaign budget earns its return.

This also reconciles with finding 1: online bookings, advance bookings and larger parties are the same underlying customer — **the planned group visit**. That, not walk-in traffic, is where VRXtra's revenue concentrates.

### 4. Demand is growing, with August and February peaks

![Demand](outputs/figures/04_demand.png)

A 3-month moving average forecasts monthly volume at **MAPE 14.5%**, beating a naive last-month baseline at 18.2%. That is a documented benchmark any future forecasting model has to beat — the point of the exercise was to establish the bar, not to claim a sophisticated model.

Note the trend and the seasonality are confounded here: the business grew substantially over the period, so the August and February peaks cannot be cleanly separated from underlying growth on 14 months of data.

### 5. A null result worth reporting

Repeat rate is 11.7% overall. It looks higher for staff-assisted customers (12.7% vs 11.2%) and for Cambridge (12.0% vs 11.4%) — but neither difference survives a two-proportion z-test (**p = 0.35** and **p = 0.69**).

I have kept these in rather than dropping them, because the null is itself informative: **repeat behaviour is not driven by where or how a customer was acquired.** If you want more repeat business here, acquisition channel is the wrong lever to pull.

---

## Method

| Step | File | What it does |
|---|---|---|
| Profile | `src/00_profile_data.py` | Schema, date coverage, missingness, automated personal-data flagging |
| Clean | `src/01_clean.py` | Pseudonymisation, category fixes, derived features |
| Analyse | `src/02_analysis.py` | Five analyses, significance tests, figures |
| Holidays | `src/04_school_holidays.py` | Natural experiment: does the midweek gap survive the school holidays? |
| SQL | `sql/*.sql` → `src/03_run_sql.py` | Seven analytical queries; results published to `outputs/sql/` with revenue indexed |
| Model | `outputs/Watford_Online_Shift_Model.xlsx` | Excel scenario model sizing the Watford recommendation, with a two-way sensitivity grid and a documented assumptions tab |

### The SQL layer

Seven queries in [`sql/`](sql/), run through DuckDB so they execute against the data file with no server:

| Query | What it answers |
|---|---|
| `01_branch_channel_quarterly` | Walk-in vs advance revenue by site and quarter |
| `02_weekday_weekend_audit` | Weekday/weekend revenue split — grouped on **session** date, not booking date |
| `03_cumulative_revenue_mom` | YTD running total and month-on-month growth (`SUM() OVER`, `LAG`) |
| `04_customer_retention` | Repeat-guest rate by site and product |
| `05_lead_time_segments` | Booking horizon buckets — **the query that reversed finding 3** |
| `06_product_persona` | Product mix and revenue contribution by traffic segment |
| `07_hourly_demand` | Day-of-week × hour demand, for staffing |

**Reconciliation.** The base view filters cancelled bookings, which reconciles these results to the source system exactly: **2,135 bookings, £180,081.98 net revenue, £0.00 variance.** Without that filter the totals run £944.99 high — the 11 cancelled bookings.

**Provenance, stated honestly.** These queries are reconstructions. The originals were written against the same data but were not retained. They are validated against the original result sets on every column that indexing does not affect: **31/31 monthly booking counts and 31/31 month-on-month growth percentages match; 17/17 retention rates and unique-guest counts match.** Where revenue appears, it is indexed here and absolute in the originals, so those columns are not directly comparable by design.

**Derived features:** booking lead time (`session_at − created_at`), booking channel, day-of-week, customer booking sequence, repeat flag.

---

## Data governance

This handles a real business's commercial data, so the handling matters as much as the analysis:

- **Personal data removed at source.** The raw export's `Created By` column contained 18 identifiable staff names alongside their individual booking counts. Every name is mapped to a stable `Staff_NN` pseudonym before analysis. The lookup never leaves the local machine.
- **Individual staff performance is not published.** The publishable view is the aggregate Online vs staff-assisted split, which is more analytically useful anyway.
- **Raw data is never committed.** `.gitignore` excludes `data/raw/`, `data/processed/` and all loose CSV/XLSX from the first commit onward.
- **All published revenue is indexed, never absolute.** VRXtra approved publication of findings, not of their commercial numbers.

Worth noting: my keyword-based personal-data detector **did not** flag `Created By`, because the column name contains no obvious PII term. It was caught by manually inspecting the values. Automated PII detection is a first pass, not a guarantee.

---

## Limitations

Stated plainly, because they bound what these findings can support:

- **No campaign or promotion field.** There is no intervention marker in the data, so no promotional lift analysis is possible. I have not manufactured one. A proper test design is the appropriate next step instead.
- **Small repeat base.** 217 repeat customers over 15 months. Enough for an overall rate, not enough for cohort retention curves that would mean anything.
- **Cancellations are 0.5%** (11 bookings) — too few to analyse.
- **Partial months excluded.** The export starts 11 Jan 2025 and ends 14 Apr 2026; both boundary months are incomplete and are dropped from all trend analysis. Including them shows a fake collapse at each end.
- **4.1% of lead times were negative** and set to null — likely a logging artefact in the source system.

## What I would do next

1. **Target midweek at audiences the school calendar does not govern** — corporate team socials and away-days, university groups, school trips. Do *not* run broad midweek discounting in term time: 91% of the gap closes on its own in the holidays, so term-time midweek is a structural constraint, not a demand problem. Save family-focused midweek promotion for the holidays, when that audience is actually free.
2. **Run a test at Watford** to move walk-in demand online — QR-code booking at the door, or a small online-only incentive. The baseline conversion and variance needed to size that experiment are in this dataset.
3. **Add a campaign field** to the booking system. Without it, no marketing activity here is measurable, which is the single biggest gap in VRXtra's data.
4. **Revisit seasonality** once 24+ months are available and growth can be separated from underlying business growth.

---

## Reproducing

```bash
pip install pandas numpy matplotlib pyarrow
python3 src/00_profile_data.py data/raw/<your-export>.csv
python3 src/01_clean.py
python3 src/02_analysis.py
```

Raw data is not included in this repository, for the reasons above.

**Stack:** Python (pandas, numpy, matplotlib) · SQL · Tableau

---

*Prithvijeet Kulkarni — MSc International Business with Business Analytics, Anglia Ruskin University. Analysis published with VRXtra's permission; all figures indexed and anonymised.*
