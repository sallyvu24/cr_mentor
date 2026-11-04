# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Student-Heavy Rental Corridors in Sydney: What Do New-Lease Rents Show?
# ### An exploratory analysis of NSW rental bond lodgements, 2018 and 2021–2026
#
# **Location:** Greater Sydney, New South Wales  |  **Tools:** Python · pandas · DuckDB · GeoPandas · Matplotlib · Seaborn · SciPy
#
# ---
# ## Project overview
#
# International education is concentrated around a small number of campuses in inner Sydney. Councils that host those campuses are
# asked to say something about student housing, but the evidence they hold is mostly counts of student-accommodation rooms and
# anecdotes. This project asks a narrower, data-driven question: **do rents on newly signed leases near campuses behave
# differently from rents in comparable flat markets away from campuses, and how sure can we be?**
#
# It is an **exploratory, descriptive analysis**. It does not build a predictive model, and it avoids causal claims that the data cannot support.
#
# ## End user and decision
#
# **End user:** a strategic planning / housing policy officer at the City of Sydney (supporting the Housing for All Working Group).
# On 20 February 2023 Council unanimously asked its CEO for advice on strategies to address the housing and cost-of-living
# pressures faced by students and referred the issue to that working group (Item 13.3, *Affordable Student Accommodation Shortage*).
# The 2026 federal settings for international student places also link growth in university allocations to the provision of
# student accommodation ([Department of Education](https://www.education.gov.au/managed-system-international-education/2026-managed-growth-settings)).
#
# **Decisions this analysis informs**
# 1. Which inner-Sydney corridors deserve deeper investigation of student-related rental pressure.
# 2. How strongly the evidence can be worded in a briefing (a calibrated statement, not an overstated one).
# 3. What additional data the Council should request (for example, student numbers by suburb).
#
# ## Analytical questions
#
# | | Question | Method |
# |---|---|---|
# | **RQ1 – What happened?** | How did new-lease rents change in each market segment across the phases of student flows, and is there a seasonal pattern tied to the academic calendar? | Monthly time series, phase tables, detrended seasonal profile |
# | **RQ2 – Where?** | Which postcodes and corridors saw faster or slower rent growth? | Choropleth maps, corridor summaries |
# | **RQ3 – Association** | Do postcodes with higher exposure to campus activity show different rent growth than comparable low-exposure postcodes? | Tier comparison, cluster bootstrap, rank correlation |
# | **RQ4 – Priority** | Which corridors warrant further investigation, and how much weight can that carry? | Corridor table gated by evidence grade |
#
# ## Scope
# - **Place:** Greater Sydney (247 postcodes in the 14 "Sydney – …" SA4 regions; Central Coast is excluded).
# - **Period:** 2018 (pre-COVID baseline) and January 2021 to September 2026. **2019–2020 is not available** in the files found.
# - **Segments:** studio/1-bedroom flats (`f01`) and 2-bedroom flats (`f2`); 3–4 bedroom houses are used for context.
#
# ## Data sources
#
# | Source | Role | Granularity | Coverage | Notes |
# |---|---|---|---|---|
# | NSW Fair Trading – Rental bond lodgements | **Outcome:** new-lease weekly rent | One row per bond | 2018; 2021–09/2026 | CC-BY; 2018 file comes from a data.nsw mirror |
# | CRICOS (Locations, Courses, Course-Locations, Institutions) | Campus locations and course levels | Course × location | Snapshot 2026-09 | No student numbers |
# | Dept of Education – enrolments by SA4 | Student distribution by place of study | SA4 × sector × field | Year to Dec 2025 | Aggregate; counts below 5 suppressed |
# | Home Affairs – BP0015 student visas granted | Timing of student inflows | Month × state × sector | 2005-06 to 2026-09 | Aggregate; visas granted, not students present |
# | ABS – POA boundaries and correspondences | Geography | Postcode polygons, population-weighted ratios | ASGS Edition 3 | Postcode areas approximate postcodes |
# | NSW Planning Portal – Online DA API | Context: housing supply proposals | One row per DA | January and July of each year, 2022–2026 (sampled) | Proposals, not completions |
# | Inside Airbnb – Sydney | Context: short- and mid-term stays | One row per listing | Snapshot 17 Sep 2026 | No history |
#
# ## Unit of analysis
# - Cleaning and descriptive statistics: **one bond lodgement**.
# - Comparisons and tests: **postcode × segment**, using the median new-lease rent in each phase.
#
# ## Evidence grading (fixed before looking at results)
#
# Because the data are observational and the exposure measure is partly modelled, every association is graded:
#
# | Grade | Rule | Reading |
# |---|---|---|
# | **A** | In at least 2 of the 3 post-closure windows the 90% cluster-bootstrap interval for the High-minus-Low gap excludes zero; at least 80% of alternative exposure definitions agree in sign; the sign survives dropping any single neighbourhood cluster in at least 90% of cases | A stable association worth taking forward |
# | **B** | At least one window excludes zero and at least 60% of alternative exposure definitions agree | A signal that depends on the choice of window or definition |
# | **C** | Anything else | Cannot be distinguished from the common market trend |
#
# No grade implies causation.
#
# ## Contents
# 1. Setup · 2. Data understanding and quality · 3. Cleaning and preparation · 4. RQ1 (rents over time, seasonality) · 5. RQ2 (where) ·
# 6. RQ3 (association with exposure) · 7. RQ4 (corridors) · 8. Robustness · 9. Context · 10. Findings, recommendations and limitations

# %% [markdown]
# ---
# # 1. Setup and data loading

# %%
from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import geopandas as gpd
from scipy import stats
from IPython.display import Markdown, display

warnings.filterwarnings("ignore", category=FutureWarning)

# Locate the data folder (contains processed/ and raw/) whether the notebook runs from notebooks/ or elsewhere.
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "processed").exists())
PROC, RAW = ROOT / "processed", ROOT / "raw"
AIRBNB_DIR = ROOT.parent / "inside_airbnb_data"
SEED = 42

pd.set_option("display.max_columns", 40)
pd.set_option("display.width", 200)
pd.set_option("display.float_format", lambda v: f"{v:,.2f}")
sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams.update({"figure.dpi": 110, "axes.titleweight": "bold", "axes.titlesize": 12, "axes.spines.top": False,
                     "axes.spines.right": False})

# One colour per exposure group, used consistently in every chart.
COLORS = {"City of Sydney": "#1b4f72", "Comparator – High": "#c0392b", "Comparator – Mid": "#e59866",
          "Comparator – Low": "#7f8c8d"}
TIER_COLORS = {"Low": "#7f8c8d", "Mid": "#e59866", "High": "#c0392b"}

def md(text: str) -> None:
    """Render a string as Markdown (used for findings that embed computed numbers)."""
    display(Markdown(text))

print(f"pandas {pd.__version__} | numpy {np.__version__} | duckdb {duckdb.__version__} | geopandas {gpd.__version__}")
print("Data folder:", ROOT)

# %% [markdown]
# # 2. Data understanding and quality assessment
#
# ## 2.1 Rental bond lodgements (the outcome data)
#
# Each row of the Fair Trading files is one bond lodged at the start of a tenancy. The data therefore describe **new leases**
# (the market a person moving house meets), not the rents paid by everyone who already rents. The raw table below was built by
# stacking 62 monthly and annual workbooks; the 2021 annual file plus the 2022–2026 monthly files are used for analysis
# because the annual and monthly files overlap from 2022.

# %%
bond_raw = pd.read_parquet(PROC / "bond_lodgements_raw.parquet",
                           columns=["date", "postcode", "dwelling", "bedrooms", "rent", "src_file", "file_kind"])
print(f"Rows: {len(bond_raw):,} | files: {bond_raw.src_file.nunique()} (annual: "
      f"{bond_raw.loc[bond_raw.file_kind == 'annual', 'src_file'].nunique()}, monthly: "
      f"{bond_raw.loc[bond_raw.file_kind == 'monthly', 'src_file'].nunique()})")
bond_raw.head()

# %%
bond_raw.tail(3)

# %%
bond_raw.info()

# %% [markdown]
# **Overlap check.** Annual and monthly files cover the same bonds from 2022. If they agree, using one source avoids double counting.

# %%
ov = (bond_raw[bond_raw.date.dt.year.between(2022, 2025)]
      .assign(year=lambda d: d.date.dt.year)
      .groupby(["year", "file_kind"]).size().unstack())
ov["annual / monthly"] = ov["annual"] / ov["monthly"]
ov

# %% [markdown]
# The annual and monthly files hold essentially the same rows, so the analysis set is the **2021 annual file plus the monthly files from January 2022**.

# %%
is_2021_annual = (bond_raw.file_kind == "annual") & (bond_raw.date.dt.year == 2021)
is_monthly_2022 = (bond_raw.file_kind == "monthly") & (bond_raw.date >= "2022-01-01")
bond_src = bond_raw[is_2021_annual | is_monthly_2022].copy()
print(f"Analysis set before cleaning: {len(bond_src):,} rows | {bond_src.date.min().date()} to {bond_src.date.max().date()}")

# %% [markdown]
# ### Missing values, codes and ranges

# %%
miss = bond_src[["rent", "bedrooms"]].isna()
quality = pd.DataFrame({"missing": miss.sum(), "missing %": (miss.mean() * 100).round(2)})
display(quality)
print("Dwelling type codes:\n", bond_src.dwelling.value_counts(dropna=False).to_string())

# %% [markdown]
# `U` means "unknown" in the source legend (dwelling, bedrooms and rent). A small number of rows carry other codes (`1`, `3`, `P`, `G` …) that the legend does not define; they are treated as invalid.

# %%
num = bond_src[["bedrooms", "rent"]].describe(percentiles=[.01, .05, .5, .95, .99])
num

# %% [markdown]
# ### Duplicates
#
# The files have no bond identifier. Two different bonds can legitimately share the same date, postcode, dwelling type, bedrooms and rent
# (common for studios in the same building), so exact duplicates are **not** removed. We measure how common they are and why dropping them would bias counts.

# %%
dup_key = ["date", "postcode", "dwelling", "bedrooms", "rent"]
n_dup = bond_src.duplicated(subset=dup_key).sum()
print(f"Rows identical on all five fields to an earlier row: {n_dup:,} ({n_dup / len(bond_src):.1%})")
dup_by_dw = (bond_src[bond_src.duplicated(subset=dup_key, keep=False)].dwelling.value_counts(normalize=True).head(4) * 100).round(1)
print("Share of duplicated rows by dwelling type (%):", dup_by_dw.to_dict())

# %% [markdown]
# ### Volume over time and weekday pattern (DuckDB SQL)
#
# DuckDB queries a pandas DataFrame directly with SQL. Here it counts bonds per month, which also shows whether any month is missing.

# %%
monthly = duckdb.sql("""
    SELECT date_trunc('month', date) AS month,
           count(*)                  AS bonds,
           round(median(rent))       AS median_rent
    FROM bond_src
    WHERE rent BETWEEN 100 AND 5000
    GROUP BY 1
    ORDER BY 1
""").df()
print("Months covered:", len(monthly), "| first:", monthly.month.min().date(), "| last:", monthly.month.max().date())

fig, ax = plt.subplots(figsize=(11, 3.6))
ax.plot(monthly.month, monthly.bonds, marker="o", ms=3, color="#1b4f72")
ax.set_title("Bond lodgements per month, all of NSW (analysis set)")
ax.set_ylabel("Bonds")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}"))
plt.show()

# %%
weekday = bond_src.date.dt.day_name().value_counts().reindex(
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
print((weekday / weekday.sum() * 100).round(1).to_string())

# %% [markdown]
# Lodgements fall almost entirely on weekdays, as expected for an administrative process. Weekend dates are rare and not a sign of a data problem.

# %% [markdown]
# ### Outliers: IQR fences versus hard limits
#
# Rent is strongly right-skewed, so the interquartile-range (IQR) rule is applied to **log rent**. We compare what the IQR rule would flag with the
# fixed plausibility limits ($100–$5,000 a week) used in cleaning.

# %%
def iqr_bounds(s: pd.Series, k: float = 1.5) -> tuple[float, float]:
    """Return (lower, upper) Tukey fences for a numeric series: Q1 - k*IQR and Q3 + k*IQR."""
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr

tmp = bond_src.dropna(subset=["rent"]).query("rent > 0").copy()
tmp["log_rent"] = np.log(tmp.rent)
lo, hi = iqr_bounds(tmp.log_rent)
tmp["iqr_flag"] = ~tmp.log_rent.between(lo, hi)
tmp["hard_flag"] = ~tmp.rent.between(100, 5000)
print(f"IQR fences on log rent -> ${np.exp(lo):,.0f} to ${np.exp(hi):,.0f} per week")
print(pd.crosstab(tmp.iqr_flag, tmp.hard_flag, margins=True).rename(
    index={False: "within IQR", True: "outside IQR"}, columns={False: "within $100–5,000", True: "outside $100–5,000"}))

# %% [markdown]
# The IQR rule flags far more rows than the hard limits, mostly plausible rents at either end of the range (inner-suburb flats, large houses). Removing them would
# strip the very markets we want to study, so **only the hard-limit rule is used to drop rows**; the IQR fences are used for inspection.

# %%
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
sns.histplot(tmp.rent.clip(upper=3000), bins=80, ax=axes[0], color="#1b4f72")
axes[0].set_title("Weekly rent (clipped at $3,000)")
sns.boxplot(data=tmp[tmp.dwelling.isin(list("FHTO"))], x="dwelling", y="rent", ax=axes[1], showfliers=False, color="#85c1e9")
axes[1].set_yscale("log")
axes[1].set_title("Rent by dwelling type (log scale)")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 2.2 Other sources
#
# A compact profile function keeps the quality checks comparable across the smaller sources.

# %%
def profile(df: pd.DataFrame, name: str) -> dict:
    """One-line quality profile: shape, share of missing cells and exact duplicate rows."""
    return {"source": name, "rows": len(df), "columns": df.shape[1],
            "missing cells %": round(df.isna().mean().mean() * 100, 2), "duplicate rows": int(df.duplicated().sum())}

# --- CRICOS
cr_loc = pd.read_csv(RAW / "cricos_full" / "cricos-locations.csv", dtype=str, encoding="utf-8-sig")
cr_crs = pd.read_csv(RAW / "cricos_full" / "cricos-courses.csv", dtype=str, encoding="utf-8-sig")
cr_cl = pd.read_csv(RAW / "cricos_full" / "cricos-course-locations.csv", dtype=str, encoding="utf-8-sig")
cr_ins = pd.read_csv(RAW / "cricos_full" / "cricos-institutions.csv", dtype=str, encoding="utf-8-sig")

# --- Department of Education enrolments by SA4
doe = pd.read_excel(RAW / "doe_sa4" / "intl_student_sa4.xlsx", header=5, usecols=range(7)).dropna(subset=["State"])
doe = doe.rename(columns=lambda c: c.strip().lower().replace(" ", "_"))      # tidy column names
doe["enrolments"] = pd.to_numeric(doe["enrolments"], errors="coerce")           # "<5" cells are suppressed -> NaN

# --- BP0015 cube
bp = pd.read_parquet(PROC / "bp0015_granted_cube.parquet")

pd.DataFrame([profile(cr_cl, "CRICOS course-locations"), profile(cr_loc, "CRICOS locations"), profile(cr_crs, "CRICOS courses"),
              profile(cr_ins, "CRICOS institutions"), profile(doe, "DoE enrolments by SA4"), profile(bp, "BP0015 cube")])

# %% [markdown]
# **CRICOS join coverage.** The course-location file has no postcode, so it must be joined to the locations table. We test that the join key is reliable.

# %%
loc_u = cr_loc.drop_duplicates(["CRICOS Provider Code", "Location Name"])
joined = cr_cl.merge(loc_u[["CRICOS Provider Code", "Location Name", "Postcode"]],
                     on=["CRICOS Provider Code", "Location Name"], how="left", validate="m:1")
print(f"Course-location rows: {len(cr_cl):,} | matched to a postcode: {joined.Postcode.notna().mean():.1%}")
print("Expired courses in the courses table:", (cr_crs.Expired == 'Yes').sum())

# %% [markdown]
# **Department of Education enrolments.** Sector labels differ in spelling and case; they are normalised before use. Suppressed cells (<5) become missing values.

# %%
print("Before:", sorted(doe.sector.unique()))
doe["sector"] = doe["sector"].str.replace(r"\s+", " ", regex=True).str.strip().str.title()
print("After: ", sorted(doe.sector.unique()))
print(f"Suppressed cells: {doe.enrolments.isna().sum()} of {len(doe)}")

# %% [markdown]
# ## 2.3 Quality summary
#
# | Source | Issue found | Impact | Treatment |
# |---|---|---|---|
# | Bond lodgements | Annual and monthly files overlap from 2022 | Double counting | Use 2021 annual + 2022+ monthly |
# | Bond lodgements | `U` codes, undefined dwelling codes, implausible rents | Biased medians | Drop invalid dwellings; keep rent $100–5,000 and bedrooms 0–8 |
# | Bond lodgements | No bond ID; exact duplicates | Cannot distinguish repeats from separate bonds | Keep duplicates |
# | Bond lodgements | Postcode only; 2019–2020 missing | Coarse geography; no pre-COVID trend | Postcode-level analysis; 2018 baseline, gap disclosed |
# | CRICOS | Course-locations file lacks postcode and level | Cannot place campuses | Join to locations (100% match) and courses |
# | DoE SA4 | One year; cells <5 suppressed; place of study | Exposure is modelled, not observed | Use shares, document assumption |
# | BP0015 | Visas granted, not students present | Phases are labels | Used only to define phases |

# %% [markdown]
# # 3. Data cleaning and preparation
#
# ## 3.1 Cleaning rules and their counts
#
# The cleaning rules are expressed in SQL (DuckDB) so every row removed is accounted for. The 2018 file comes from a different source and is added first.

# %%
b18 = pd.read_csv(RAW / "nsw_bond_2018" / "rentalbond_lodgements_year_2018.csv", skiprows=3, dtype=str, encoding="utf-8-sig")
b18.columns = ["d", "postcode", "dwelling", "bedrooms", "rent"]
b18["date"] = pd.to_datetime(b18["d"], format="%d/%m/%Y", errors="coerce")
for c in ["postcode", "bedrooms", "rent"]:
    b18[c] = pd.to_numeric(b18[c], errors="coerce")
b18["dwelling"] = b18["dwelling"].str.strip()
b18 = b18.dropna(subset=["date", "postcode"])
bond_all = pd.concat([b18[["date", "postcode", "dwelling", "bedrooms", "rent"]].assign(source="2018"),
                      bond_src[["date", "postcode", "dwelling", "bedrooms", "rent"]].assign(source="2021-2026")],
                     ignore_index=True)

exposure = pd.read_csv(PROC / "exposure_postcode.csv", dtype={"poa": str, "E3_nearest_major_poa": str})
pool_df = exposure.loc[exposure.in_pool, ["poa"]]          # DataFrame so DuckDB can query it
pool_poas = pool_df["poa"]
bond_all["poa"] = bond_all.postcode.astype(int).astype(str).str.zfill(4)

cleaning_log = duckdb.sql("""
    SELECT 'raw rows (2018 + 2021-2026)'                                   AS step, count(*) AS rows FROM bond_all
    UNION ALL SELECT 'invalid dwelling code',        count(*) FROM bond_all WHERE dwelling NOT IN ('F','H','T','O','U')
    UNION ALL SELECT 'rent missing or outside 100-5,000 (valid dwelling)',  count(*) FROM bond_all
              WHERE dwelling IN ('F','H','T','O','U') AND NOT coalesce(rent BETWEEN 100 AND 5000, false)
    UNION ALL SELECT 'bedrooms missing or outside 0-8 (rest valid)',        count(*) FROM bond_all
              WHERE dwelling IN ('F','H','T','O','U') AND coalesce(rent BETWEEN 100 AND 5000, false)
                AND NOT coalesce(bedrooms BETWEEN 0 AND 8, false)
    UNION ALL SELECT 'clean rows, all NSW',          count(*) FROM bond_all
              WHERE dwelling IN ('F','H','T','O','U') AND coalesce(rent BETWEEN 100 AND 5000, false)
                AND coalesce(bedrooms BETWEEN 0 AND 8, false)
    UNION ALL SELECT 'clean rows in the 247-postcode analysis pool', count(*) FROM bond_all
              WHERE dwelling IN ('F','H','T','O','U') AND coalesce(rent BETWEEN 100 AND 5000, false)
                AND coalesce(bedrooms BETWEEN 0 AND 8, false) AND poa IN (SELECT poa FROM pool_df)
""").df()
cleaning_log["rows"] = cleaning_log["rows"].map("{:,}".format)
cleaning_log

# %% [markdown]
# ## 3.2 The analysis panel
#
# The panel produced by `scripts/06_build_panel.py` is loaded and checked against the cleaning log above. Each bond already carries its postcode's
# SA3/SA4, exposure measures, market segment and phase.

# %%
panel = pd.read_parquet(PROC / "analysis_bond_panel.parquet")
assert len(panel) == int(cleaning_log.loc[cleaning_log.step.str.contains("analysis pool"), "rows"].str.replace(",", "").iloc[0]), \
    "panel row count must equal the cleaning log"
assert panel.rent.between(100, 5000).all() and panel.bedrooms.between(0, 8).all()
assert panel.poa.isin(pool_poas).all()
print(f"Panel: {len(panel):,} bonds | {panel.poa.nunique()} postcodes | {panel.date.min().date()} to {panel.date.max().date()}")
panel[["date", "poa", "dwelling", "bedrooms", "rent", "seg", "phase", "sa3", "E2_rows_l3", "E3_dist_major_km"]].sample(5, random_state=SEED)

# %% [markdown]
# **Market segments.** Student demand is expected to be strongest in small flats, so rent is analysed by segment. 3–4 bedroom houses are used for context only.

# %%
seg_tab = (panel.groupby("seg")
           .agg(bonds=("rent", "size"), median_rent=("rent", "median"), share=("rent", lambda s: len(s) / len(panel) * 100))
           .sort_values("bonds", ascending=False))
seg_tab["share"] = seg_tab["share"].round(1)
seg_tab

# %% [markdown]
# ## 3.3 Feature scaling: putting exposure measures on one scale
#
# Several exposure variants are built from the same campus information (see 3.4). They use different units, so min–max and z-score scaling are
# applied to compare them. Rent, which is skewed, is analysed as a **log ratio** (percentage change), a log transform.

# %%
def minmax(s: pd.Series) -> pd.Series:
    """Rescale to the 0–1 range."""
    return (s - s.min()) / (s.max() - s.min())

def zscore(s: pd.Series) -> pd.Series:
    """Centre on the mean and divide by the standard deviation."""
    return (s - s.mean()) / s.std(ddof=1)

EXPOSURE_VARIANTS = {
    "E2 λ=1.5 km": "E2_rows_l1.5",
    "E2 λ=3 km (primary)": "E2_rows_l3",
    "E2 λ=5 km": "E2_rows_l5",
    "E2 equal-split λ=3 km": "E2_equal_l3",
    "E3 distance (inverted)": "E3_dist_major_km",
    "E1 SA4 share (HE)": "E1_share_he",
}
pool_pc = exposure[exposure.in_pool].copy()
pool_pc["E3_dist_major_km"] = -pool_pc["E3_dist_major_km"]          # invert so that higher always means "more exposed"
scaled = pd.DataFrame({k: minmax(pool_pc[v]) for k, v in EXPOSURE_VARIANTS.items()})
print("Min–max scaled exposure variants (summary):")
display(scaled.describe().loc[["mean", "50%", "max"]].round(3))

# %%
fig, axes = plt.subplots(1, 2, figsize=(13, 4.2))
pool_pc["E2_rows_l3"].plot.hist(bins=40, ax=axes[0], color="#1b4f72")
axes[0].set_title("E2 (λ=3 km), raw: strongly right-skewed")
axes[0].set_xlabel("Campus-weighted accessibility (thousand enrolments)")
sns.heatmap(scaled.corr(method="spearman"), annot=True, fmt=".2f", cmap="Blues", vmin=0, vmax=1, ax=axes[1], cbar=False)
axes[1].set_title("Rank correlation between exposure variants")
plt.tight_layout()
plt.show()

# %% [markdown]
# The variants are strongly related, which is expected: all of them describe proximity to the same handful of campuses. This matters for how much
# a robustness check across variants can prove (section 8).

# %% [markdown]
# ## 3.4 Geography and exposure
#
# **How exposure is built.**
# 1. Campuses are CRICOS higher-education course locations in Greater Sydney (485 campuses; 16 "major" with at least 50 HE course-location rows).
# 2. Each SA4's higher-education enrolments (Department of Education) are split across the campuses in that SA4 in proportion to their HE course-location rows. **This is an allocation assumption, not observed enrolment per campus.**
# 3. **E2** for a postcode is the sum over campuses of weight × exp(−distance / λ). **E3** is the distance to the nearest major campus. **E1** is the SA4's share of enrolments.
# 4. Distances use ABS postcode-area centroids, so resolution is about 1 km. UNSW (postcode 2052) and Macquarie (2109) have no ABS postcode area and are mapped to 2033 and 2113.

# %%
campuses = pd.read_csv(PROC / "he_campuses.csv", dtype={"poa": str, "postcode_cricos": str})
print(f"Campuses: {len(campuses)} | major (>=50 HE rows): {(campuses.he_rows >= 50).sum()}")
campuses.sort_values("w_rows", ascending=False)[
    ["Institution Name", "Location Name", "poa", "sa4", "he_rows", "w_rows"]].head(8).round(0)

# %%
POA_SHP = RAW / "abs_poa" / "shp" / "POA_2021_AUST_GDA2020.shp"
poa_gdf = gpd.read_file(POA_SHP, bbox=(150.55, -34.25, 151.45, -33.35)).rename(columns={"POA_CODE21": "poa"})[["poa", "geometry"]]
poa_gdf = poa_gdf[poa_gdf.poa.isin(pool_poas)].merge(exposure.drop(columns=["lat", "lon"]), on="poa")
cam_df = campuses.groupby("poa").agg(lat=("lat", "first"), lon=("lon", "first"), he_rows=("he_rows", "sum")).reset_index()
cam_pts = gpd.GeoDataFrame(cam_df, geometry=gpd.points_from_xy(cam_df.lon, cam_df.lat), crs=poa_gdf.crs)
cam_pts = cam_pts[(cam_pts.he_rows >= 50) & cam_pts.poa.isin(pool_poas)]

def draw_map(ax, gdf, col, title, cmap="YlOrRd", bbox=None, points=None, legend_label=""):
    """Choropleth of postcode areas; optional bounding box (zoom) and point overlay."""
    gdf.plot(column=col, cmap=cmap, linewidth=0.2, edgecolor="white", ax=ax, legend=True,
             legend_kwds={"shrink": 0.6, "label": legend_label}, missing_kwds={"color": "#e5e8e8"})
    if points is not None:
        points.plot(ax=ax, color="black", markersize=14, marker="^", zorder=5)
    if bbox:
        ax.set_xlim(bbox[0], bbox[2]); ax.set_ylim(bbox[1], bbox[3])
    ax.set_aspect(1 / np.cos(np.radians(33.85)))
    ax.set_axis_off(); ax.set_title(title)

fig, axes = plt.subplots(1, 2, figsize=(14, 6.2))
draw_map(axes[0], poa_gdf, "E2_rows_l3", "E2 exposure, Greater Sydney", points=cam_pts, legend_label="E2 (λ=3 km)")
draw_map(axes[1], poa_gdf, "E2_rows_l3", "Inner Sydney (zoom); ▲ = major campuses", bbox=(151.10, -34.00, 151.32, -33.78),
         points=cam_pts, legend_label="E2 (λ=3 km)")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 3.5 Groups used for comparison
#
# The City of Sydney's own postcodes are almost all flats and almost all within 2 km of a major campus, so they cannot be compared with each other.
# The comparison pool therefore contains **flat-heavy postcodes elsewhere in Greater Sydney** (at least 35% of 2018 bonds were flats, and at least 200
# studio/1BR and 2BR bonds in 2018). All eligible postcodes are split into tertiles of E2 (Low, Mid, High).

# %%
base = pd.read_csv(PROC / "postcode_baseline.csv", dtype={"poa": str, "E3_nearest_major_poa": str})
elig = base[base.city_of_sydney | base.comparator_candidate].copy()
elig["tier"] = pd.qcut(elig.E2_rows_l3, 3, labels=["Low", "Mid", "High"])
elig["group"] = np.where(elig.city_of_sydney, "City of Sydney", "Comparator – " + elig.tier.astype(str))

grp_tab = (elig.groupby("group")
           .agg(postcodes=("poa", "size"), flat_share_2018=("flat_share_2018", "mean"),
                median_f01_2018=("med_f01_2018", "median"), median_f2_2018=("med_f2_2018", "median"),
                E2_min=("E2_rows_l3", "min"), E2_max=("E2_rows_l3", "max"), median_dist_km=("E3_dist_major_km", "median"))
           .reindex(list(COLORS)))
grp_tab

# %% [markdown]
# Baseline rents differ by group (City of Sydney is dearer in 2018), so the analysis compares **changes**, not levels.

# %% [markdown]
# ## 3.6 Phases of student flows
#
# Phases are defined from NSW student-visa grants (primary applicants, Home Affairs BP0015), using a rolling 12-month total. Visas granted are a flow
# that leads or lags the number of students actually present, so the phase labels are working definitions.

# %%
def bp_dates(df: pd.DataFrame) -> pd.Series:
    """Convert BP0015 financial-year + month labels (e.g. '2022-23', 'M01 Jul') into calendar month starts."""
    mn = df.month.str.extract(r"M(\d+)")[0].astype(int)
    fy0 = df.fy.str[:4].astype(int)
    cal_month = ((mn + 5) % 12) + 1
    cal_year = np.where(mn <= 6, fy0, fy0 + 1)
    return pd.to_datetime(dict(year=cal_year, month=cal_month, day=1))

bp["date"] = bp_dates(bp)
nsw_primary = bp[(bp.state == "NSW") & (bp.applicant == "Primary")].groupby("date").grants.sum()
roll12 = nsw_primary.rolling(12).sum().dropna()
roll12 = roll12[roll12.index >= "2018-01-01"]

PHASES = {"0_base2018": ("2018-01-01", "2018-12-31"), "1_closure": ("2021-01-01", "2021-11-30"),
          "2_recovery": ("2021-12-01", "2023-07-31"), "3_correction": ("2023-08-01", "2024-06-30"),
          "4_plateau_decline": ("2024-07-01", "2026-09-30")}
PHASE_LABEL = {"0_base2018": "2018 baseline", "1_closure": "Closure (2021)", "2_recovery": "Recovery", "3_correction": "Correction",
               "4_plateau_decline": "Plateau & decline"}
PHASE_FILL = {"1_closure": "#d5d8dc", "2_recovery": "#d4efdf", "3_correction": "#fdebd0", "4_plateau_decline": "#fadbd8"}

fig, ax = plt.subplots(figsize=(11.5, 4.2))
ax.plot(roll12.index, roll12.values, color="#1b4f72", lw=2)
for ph, (a, b) in PHASES.items():
    if ph in PHASE_FILL:
        ax.axvspan(pd.Timestamp(a), pd.Timestamp(b), color=PHASE_FILL[ph], alpha=0.8, lw=0)
        ax.text(pd.Timestamp(a) + (pd.Timestamp(b) - pd.Timestamp(a)) / 2, ax.get_ylim()[1] * 0.97, PHASE_LABEL[ph],
                ha="center", va="top", fontsize=8)
ax.set_title("NSW student visas granted to primary applicants, rolling 12 months")
ax.set_ylabel("Visas granted")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}"))
plt.show()

quarterly = nsw_primary.resample("QS").sum()                     # monthly series -> quarterly totals
print("Latest quarters (visas granted):", {f"{d:%Y-Q}{(d.month - 1) // 3 + 1}": int(v) for d, v in quarterly.tail(4).items()})
trough, peak = roll12["2020-06-01":].idxmin(), roll12["2020-06-01":].idxmax()
print(f"Trough {trough:%b %Y}: {roll12[trough]:,.0f} | Peak {peak:%b %Y}: {roll12[peak]:,.0f} | Latest {roll12.index[-1]:%b %Y}: {roll12.iloc[-1]:,.0f}")

# %% [markdown]
# # 4. RQ1 – How did new-lease rents change?
#
# **Research question.** How did the median new-lease rent change across the phases for each market segment, in the City of Sydney and in the
# comparison tiers?
#
# ## 4.1 Monthly median rent index
#
# For each group and segment, the monthly median rent is indexed to the **2018 average = 100**. The grey gap marks 2019–2020, for which no bond files were found.

# %%
panel = panel.merge(elig[["poa", "group", "tier"]], on="poa", how="left")
panel["month"] = panel.date.dt.to_period("M").dt.to_timestamp()
SEGS = ["f01", "f2"]
SEG_LABEL = {"f01": "Studio / 1-bedroom flats", "f2": "2-bedroom flats"}

grp_month = (panel[panel.seg.isin(SEGS) & panel.group.notna()]
             .groupby(["group", "seg", "month"]).rent.median().rename("med").reset_index())
all_months = pd.date_range("2018-01-01", "2026-09-01", freq="MS")

fig, axes = plt.subplots(1, 2, figsize=(15, 4.8), sharey=True)
for ax, seg in zip(axes, SEGS):
    for g, col in COLORS.items():
        s = (grp_month[(grp_month.group == g) & (grp_month.seg == seg)].set_index("month").med.reindex(all_months))
        idx = s / s["2018"].mean() * 100                        # time-series slicing by year string
        ax.plot(idx.index, idx.rolling(3, min_periods=2).mean(), color=col, lw=2, label=g)
    ax.axvspan(pd.Timestamp("2019-01-01"), pd.Timestamp("2020-12-31"), color="#eaeded", zorder=0)
    ax.text(pd.Timestamp("2019-12-31"), ax.get_ylim()[0] + 3, "no data", ha="center", fontsize=8, color="#7b7d7d")
    ax.set_title(SEG_LABEL[seg]); ax.set_ylabel("Median rent, 2018 = 100")
axes[0].legend(frameon=False, fontsize=8)
fig.suptitle("Median new-lease rent index by exposure group (3-month rolling mean)", y=1.02, fontweight="bold")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 4.2 Median weekly rent by phase (AUD)
#
# The same medians are computed twice, once in pandas and once in SQL, and compared. This is the table that later comparisons are built on.

# %%
cell_pd = (panel[panel.seg.isin(SEGS + ["h34"])]
           .groupby(["poa", "seg", "phase"]).agg(n=("rent", "size"), med=("rent", "median")).reset_index())

cell_sql = duckdb.sql("""
    SELECT poa, seg, phase, count(*) AS n, median(rent) AS med
    FROM panel
    WHERE seg IN ('f01','f2','h34')
    GROUP BY poa, seg, phase
""").df()
chk = cell_pd.merge(cell_sql, on=["poa", "seg", "phase"], suffixes=("_pd", "_sql"), validate="1:1")
assert np.allclose(chk.med_pd, chk.med_sql) and (chk.n_pd == chk.n_sql).all()
print(f"pandas and SQL agree on {len(chk):,} postcode × segment × phase medians")

grp_phase = (panel[panel.seg.isin(SEGS) & panel.group.notna()]
             .groupby(["seg", "group", "phase"]).rent.median().unstack("phase")[list(PHASES)]
             .rename(columns=PHASE_LABEL).reindex(list(COLORS), level=1))
grp_phase

# %% [markdown]
# ## 4.3 Finding for RQ1

# %%
cum = (grp_phase["Plateau & decline"] / grp_phase["2018 baseline"] - 1) * 100
dip = (grp_phase["Closure (2021)"] / grp_phase["2018 baseline"] - 1) * 100
lines = []
for seg in SEGS:
    c, d = cum.loc[seg], dip.loc[seg]
    lines.append(f"- **{SEG_LABEL[seg]}:** during closure the median new-lease rent was {d.min():+.0f}% to {d.max():+.0f}% versus 2018 across the groups; "
                 f"by the plateau-and-decline phase it was {c.min():+.0f}% to {c.max():+.0f}% above 2018 "
                 f"(City of Sydney {c['City of Sydney']:+.0f}%, low-exposure comparators {c['Comparator – Low']:+.0f}%).")
md("**Key finding – RQ1.** Rents on newly signed flat leases fell in 2021 and then rose strongly in every group, so most of the movement is a "
   "market-wide cycle shared by high- and low-exposure areas.\n\n" + "\n".join(lines) +
   "\n\nGroup differences in the cumulative size of these movements are small compared with the common movement. The 2021 dip differed "
   "more between groups, and RQ3 examines that directly instead of reading the charts by eye.")

# %% [markdown]
# ## 4.4 Seasonality: is there a student-calendar signature?
#
# Student demand is concentrated around the start of the academic year (February–March, and to a lesser extent July). If campus-related demand
# matters for new-lease rents, High-exposure postcodes might show a seasonal peak in those months that Low-exposure postcodes do not.
#
# **Method.** For each tier and segment the monthly median rent is logged, the centred 12-month moving average (the trend) is subtracted, and the
# remainder is averaged by calendar month. This needs a full year of context on each side, so the first and last six months drop out.

# %%
def detrended_seasonal(s: pd.Series) -> pd.Series:
    """Log monthly median minus its centred 12-month moving average, in percent."""
    ls = np.log(s)
    return (ls - ls.rolling(12, center=True, min_periods=12).mean()).dropna() * 100

post = panel[(panel.date >= "2021-01-01") & panel.tier.isin(["High", "Low"]) & panel.seg.isin(SEGS)]
tier_month = post.groupby(["tier", "seg", "month"], observed=True).rent.median()
seas = {}
for (tier, seg), ser in tier_month.groupby(level=[0, 1]):
    seas[(str(tier), seg)] = detrended_seasonal(ser.droplevel([0, 1]))
season_profile = pd.DataFrame({k: v.groupby(v.index.month).mean() for k, v in seas.items()})
season_profile.columns = pd.MultiIndex.from_tuples(season_profile.columns, names=["tier", "segment"])

fig, axes = plt.subplots(1, 2, figsize=(13, 4.2), sharey=True)
for ax, seg in zip(axes, SEGS):
    for tier in ["High", "Low"]:
        ax.plot(season_profile.index, season_profile[(tier, seg)], marker="o", lw=2, color=TIER_COLORS[tier], label=f"{tier} exposure")
    ax.axhline(0, color="#7b7d7d", lw=0.8, ls=":")
    ax.set_xticks(range(1, 13)); ax.set_xticklabels(list("JFMAMJJASOND"))
    ax.set_title(SEG_LABEL[seg]); ax.set_xlabel("Month of lodgement")
axes[0].set_ylabel("Rent relative to 12-month trend (%)")
axes[0].legend(frameon=False)
fig.suptitle("Average seasonal pattern in new-lease rents, 2021–2026", y=1.02, fontweight="bold")
plt.tight_layout()
plt.show()

# %% [markdown]
# **Is the February peak consistent from year to year?** The High-minus-Low difference in the detrended series is averaged over February–March for each year,
# and compared with July–August as a reference period.

# %%
rows = []
for seg in SEGS:
    d = (seas[("High", seg)] - seas[("Low", seg)]).rename("gap")
    for yr, g in d.groupby(d.index.year):
        rows.append({"segment": seg, "year": yr,
                     "Feb–Mar gap (pp)": g[g.index.month.isin([2, 3])].mean(),
                     "Jul–Aug gap (pp)": g[g.index.month.isin([7, 8])].mean()})
season_years = pd.DataFrame(rows)
season_years.pivot(index="year", columns="segment", values=["Feb–Mar gap (pp)", "Jul–Aug gap (pp)"]).round(1)

# %%
k_pos = {seg: int((season_years[(season_years.segment == seg)]["Feb–Mar gap (pp)"].dropna() > 0).sum()) for seg in SEGS}
n_yrs = {seg: int(season_years[(season_years.segment == seg)]["Feb–Mar gap (pp)"].notna().sum()) for seg in SEGS}
feb = {(t, seg): season_profile.loc[2, (t, seg)] for t in ["High", "Low"] for seg in SEGS}
SEASON_TEXT = (f"Studio/1BR rents in High-exposure postcodes sit {feb[('High','f01')]:+.1f}% relative to trend in February, against {feb[('Low','f01')]:+.1f}% in Low-exposure postcodes; "
               f"for 2BR flats the figures are {feb[('High','f2')]:+.1f}% and {feb[('Low','f2')]:+.1f}%. The High-minus-Low February–March gap was positive in "
               f"{k_pos['f01']} of {n_yrs['f01']} years for studio/1BR and {k_pos['f2']} of {n_yrs['f2']} years for 2BR flats.")
md("**Key finding – seasonality.** " + SEASON_TEXT + " A February peak that appears in High- but not Low-exposure postcodes is consistent with demand "
   "tied to the start of the academic year. It is not proof: inner-city areas may also have a general summer-to-autumn leasing cycle, and only five annual "
   "cycles are available, so this is a lead to test with better data (for example term-address counts), not a conclusion.")

# %% [markdown]
# # 5. RQ2 – Where did rents change most?
#
# **Research question.** Which postcodes and corridors saw faster or slower rent growth?
#
# ## 5.1 Postcode-level changes
#
# For each postcode and segment, the change between phases is measured as 100 × ln(median rent in phase B ÷ median rent in phase A), which is a
# percentage change that is symmetric and comparable across rent levels. A postcode-segment contributes only if **both phases have at least
# `MIN_N` bonds**; otherwise a median from a handful of leases would dominate the result.

# %%
MIN_N = 30
TRANS = {"T0": ("0_base2018", "1_closure"), "T1": ("1_closure", "2_recovery"), "T2": ("2_recovery", "3_correction"),
         "T3": ("3_correction", "4_plateau_decline"), "CUM": ("0_base2018", "4_plateau_decline")}
TRANS_LABEL = {"T0": "2018 → closure", "T1": "closure → recovery", "T2": "recovery → correction", "T3": "correction → plateau", "CUM": "2018 → plateau (cumulative)"}
PRIMARY_WINDOWS = ["T1", "T2", "T3"]

def build_changes(cell: pd.DataFrame, min_n: int = MIN_N) -> pd.DataFrame:
    """Percentage (log) change in median rent between phases, per postcode × segment, requiring ≥ min_n bonds in both phases."""
    med = cell.pivot(index=["poa", "seg"], columns="phase", values="med")
    n = cell.pivot(index=["poa", "seg"], columns="phase", values="n")
    parts = []
    for key, (a, b) in TRANS.items():
        ok = (n[a] >= min_n) & (n[b] >= min_n)
        parts.append((100 * np.log(med[b] / med[a])).where(ok).rename(key))
    out = pd.concat(parts, axis=1).reset_index().melt(id_vars=["poa", "seg"], var_name="trans", value_name="chg")
    return out.dropna(subset=["chg"])

chg = build_changes(cell_pd).merge(
    elig[["poa", "sa3", "sa4", "lga_dom", "city_of_sydney", "tier", "group", "E2_rows_l3", "E3_dist_major_km"]], on="poa", how="inner")
print(f"Postcode × segment × transition observations: {len(chg):,}")
print(chg.groupby(["seg", "trans"]).poa.nunique().unstack().loc[SEGS + ["h34"]].to_string())

# %% [markdown]
# ## 5.2 Maps

# %%
cum_f01 = chg[(chg.seg == "f01") & (chg.trans == "CUM")][["poa", "chg"]].rename(columns={"chg": "cum_f01"})
cum_f2 = chg[(chg.seg == "f2") & (chg.trans == "CUM")][["poa", "chg"]].rename(columns={"chg": "cum_f2"})
map_gdf = poa_gdf.merge(cum_f01, on="poa", how="left").merge(cum_f2, on="poa", how="left")
inner = (151.10, -34.00, 151.32, -33.78)

fig, axes = plt.subplots(1, 2, figsize=(14, 6.2))
draw_map(axes[0], map_gdf, "cum_f01", "Studio/1BR rent change, 2018 → plateau (%)", cmap="viridis", bbox=inner, points=cam_pts, legend_label="% change")
draw_map(axes[1], map_gdf, "cum_f2", "2BR rent change, 2018 → plateau (%)", cmap="viridis", bbox=inner, points=cam_pts, legend_label="% change")
plt.tight_layout()
plt.show()
print("Grey areas have too few bonds in 2018 or in the plateau phase for a reliable median.")

# %% [markdown]
# ## 5.3 Corridors (SA3 neighbourhoods)
#
# SA3 regions are used as neighbourhood "corridors": they are large enough to hold several postcodes and small enough to keep local character.

# %%
corr = (chg[(chg.trans == "CUM") & chg.seg.isin(SEGS)]
        .groupby(["sa3", "seg"]).agg(postcodes=("poa", "nunique"), median_chg=("chg", "median")).reset_index()
        .pivot(index="sa3", columns="seg", values=["postcodes", "median_chg"]))
corr.columns = [f"{a}_{b}" for a, b in corr.columns]
corr = corr[corr.postcodes_f01 >= 3].sort_values("median_chg_f01", ascending=False)

fig, ax = plt.subplots(figsize=(10, 6))
y = np.arange(len(corr))
ax.barh(y - 0.2, corr.median_chg_f01, height=0.4, color="#1b4f72", label=SEG_LABEL["f01"])
ax.barh(y + 0.2, corr.median_chg_f2, height=0.4, color="#85c1e9", label=SEG_LABEL["f2"])
ax.set_yticks(y); ax.set_yticklabels(corr.index); ax.invert_yaxis()
ax.set_xlabel("Median change in new-lease rent, 2018 → plateau (%)")
ax.set_title("Cumulative rent change by corridor (SA3, at least 3 postcodes)")
ax.legend(frameon=False)
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 5.4 Finding for RQ2

# %%
top = corr.median_chg_f01.idxmax(); bot = corr.median_chg_f01.idxmin()
inner_name = "Sydney Inner City"
inner_row = corr.loc[inner_name] if inner_name in corr.index else None
txt = (f"Across {len(corr)} corridors, the median cumulative change in studio/1BR new-lease rent from 2018 to the plateau-and-decline phase "
       f"ranges from {corr.median_chg_f01.min():+.0f}% ({bot}) to {corr.median_chg_f01.max():+.0f}% ({top}).")
if inner_row is not None:
    rank = int((corr.median_chg_f01 > inner_row.median_chg_f01).sum() + 1)
    txt += (f" The Sydney Inner City corridor, which contains most City of Sydney postcodes, changed by {inner_row.median_chg_f01:+.0f}% "
            f"(rank {rank} of {len(corr)}).")
md("**Key finding – RQ2.** " + txt + " Rent growth is geographically widespread, not confined to the campus areas. Whether the spread across "
   "corridors lines up with campus exposure is tested next.")

# %% [markdown]
# # 6. RQ3 – Is exposure associated with different rent growth?
#
# **Research question.** Among comparable flat-heavy postcodes, do those with High campus exposure show different rent growth than those with Low exposure?
#
# **Method.**
# - **Gap:** median change in the High tier minus median change in the Low tier, in percentage points.
# - **Uncertainty:** neighbouring postcodes share local conditions, so a postcode-level bootstrap would be too optimistic. Instead the bootstrap
#   **resamples whole SA3 corridors** (2,000 times) and reports a 90% interval.
# - **Rank correlation:** Spearman ρ between E2 and the change, across all eligible postcodes.
# - **Naive permutation p-value:** shown for reference only; it ignores spatial dependence and is therefore optimistic.

# %%
N_BOOT = 2000

def tier_gap_arrays(vals: np.ndarray, tiers: np.ndarray) -> float:
    """High-minus-Low gap in medians; NaN if either tier has fewer than 3 postcodes."""
    hi, lo = vals[tiers == "High"], vals[tiers == "Low"]
    return np.median(hi) - np.median(lo) if len(hi) >= 3 and len(lo) >= 3 else np.nan

def cluster_bootstrap(d: pd.DataFrame, stat, cluster: str = "sa3", n_boot: int = N_BOOT, seed: int = SEED):
    """Resample whole clusters with replacement; return the 5th/95th percentiles of `stat(values, tiers, exposure)`."""
    rng = np.random.default_rng(seed)
    parts = [(g.chg.to_numpy(), g.tier.astype(str).to_numpy(), g.E2_rows_l3.to_numpy()) for _, g in d.groupby(cluster)]
    reps = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(parts), len(parts))
        v = np.concatenate([parts[i][0] for i in pick]); t = np.concatenate([parts[i][1] for i in pick]); e = np.concatenate([parts[i][2] for i in pick])
        s = stat(v, t, e)
        if np.isfinite(s):
            reps.append(s)
    return (np.percentile(reps, 5), np.percentile(reps, 95)) if len(reps) >= 200 else (np.nan, np.nan)

def rho_stat(v, t, e) -> float:
    return stats.spearmanr(e, v).statistic if len(v) > 10 and np.std(e) > 0 else np.nan

def gap_stat(v, t, e) -> float:
    return tier_gap_arrays(v, t)

def permutation_p(d: pd.DataFrame, n_perm: int = 5000, seed: int = SEED) -> float:
    """Two-sided naive permutation p-value for Spearman rho (shuffles exposure across postcodes)."""
    rng = np.random.default_rng(seed)
    obs = stats.spearmanr(d.E2_rows_l3, d.chg).statistic
    e = d.E2_rows_l3.to_numpy(); v = d.chg.to_numpy()
    perm = np.array([stats.spearmanr(rng.permutation(e), v).statistic for _ in range(n_perm)])
    return float((np.abs(perm) >= abs(obs)).mean())

# %%
rows = []
for seg in SEGS:
    for tr in TRANS:
        d = chg[(chg.seg == seg) & (chg.trans == tr)]
        gap = tier_gap_arrays(d.chg.to_numpy(), d.tier.astype(str).to_numpy())
        lo, hi = cluster_bootstrap(d, gap_stat)
        rho = stats.spearmanr(d.E2_rows_l3, d.chg).statistic
        rlo, rhi = cluster_bootstrap(d, rho_stat, n_boot=1000)
        rows.append({"seg": seg, "trans": tr, "n_postcodes": len(d), "n_High": int((d.tier == "High").sum()), "n_Low": int((d.tier == "Low").sum()),
                     "gap_pp": gap, "gap_lo": lo, "gap_hi": hi, "rho": rho, "rho_lo": rlo, "rho_hi": rhi, "p_perm_naive": permutation_p(d, 2000)})
res = pd.DataFrame(rows)
res["excludes_0"] = (res.gap_lo > 0) | (res.gap_hi < 0)
res_show = res.assign(window=res.trans.map(TRANS_LABEL))[["seg", "window", "n_postcodes", "n_High", "n_Low", "gap_pp", "gap_lo", "gap_hi", "rho", "rho_lo", "rho_hi", "p_perm_naive", "excludes_0"]]
res_show.round(2)

# %% [markdown]
# ## 6.1 Distribution of changes by tier

# %%
fig, axes = plt.subplots(2, 5, figsize=(20, 7.5), sharey="row")
for i, seg in enumerate(SEGS):
    for j, tr in enumerate(TRANS):
        ax = axes[i, j]
        d = chg[(chg.seg == seg) & (chg.trans == tr)]
        sns.boxplot(data=d, x="tier", y="chg", order=["Low", "Mid", "High"], palette=TIER_COLORS, showfliers=False, ax=ax, width=0.6)
        sns.stripplot(data=d, x="tier", y="chg", order=["Low", "Mid", "High"], color="black", size=2.5, alpha=0.45, ax=ax)
        ax.axhline(0, color="#7b7d7d", lw=0.8, ls=":")
        ax.set_title(f"{SEG_LABEL[seg].split(' ')[0]}  |  {TRANS_LABEL[tr]}", fontsize=9)
        ax.set_xlabel(""); ax.set_ylabel("Change in median rent (%)" if j == 0 else "")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 6.2 Exposure against change

# %%
fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
for ax, seg in zip(axes, SEGS):
    d = chg[(chg.seg == seg) & (chg.trans == "CUM")].copy()
    sns.scatterplot(data=d, x="E2_rows_l3", y="chg", hue="city_of_sydney", palette={True: "#1b4f72", False: "#aab7b8"}, s=45, ax=ax, legend=False)
    d["bin"] = pd.qcut(d.E2_rows_l3, 6, duplicates="drop")
    bins = d.groupby("bin", observed=True).agg(x=("E2_rows_l3", "median"), y=("chg", "median"))
    ax.plot(bins.x, bins.y, color="#c0392b", marker="o", lw=2, label="binned median")
    rho = res[(res.seg == seg) & (res.trans == "CUM")].rho.iloc[0]
    ax.set_title(f"{SEG_LABEL[seg]}  (Spearman ρ = {rho:+.2f})")
    ax.set_xlabel("E2 exposure (λ=3 km)"); ax.set_ylabel("Change 2018 → plateau (%)")
    ax.legend(frameon=False)
plt.tight_layout()
plt.show()
print("Dark blue points are City of Sydney postcodes.")

# %% [markdown]
# ## 6.3 Does the signal differ between small flats and 2-bedroom flats?
#
# If student demand mattered specifically, the High-minus-Low gap should be larger for studio/1BR than for 2BR flats. For each postcode the difference
# between its studio/1BR change and its 2BR change is computed, then compared across tiers.

# %%
wide = chg[chg.seg.isin(SEGS)].pivot_table(index=["poa", "trans"], columns="seg", values="chg").dropna().reset_index()
wide["chg"] = wide.f01 - wide.f2
wide = wide.merge(elig[["poa", "sa3", "tier", "E2_rows_l3", "city_of_sydney"]], on="poa")
contrast = []
for tr in TRANS:
    d = wide[wide.trans == tr]
    lo, hi = cluster_bootstrap(d, gap_stat)
    contrast.append({"window": TRANS_LABEL[tr], "n_postcodes": len(d), "gap_pp (f01 − f2)": tier_gap_arrays(d.chg.to_numpy(), d.tier.astype(str).to_numpy()), "lo": lo, "hi": hi})
contrast = pd.DataFrame(contrast)
contrast["excludes_0"] = (contrast.lo > 0) | (contrast.hi < 0)
contrast.round(2)

# %% [markdown]
# ## 6.4 Robustness inputs for the evidence grade
#
# The grade (defined at the start of the notebook) needs two further checks.
# 1. **Alternative exposure definitions:** the same rank correlation computed with each exposure variant, segment and window (60 specifications).
# 2. **Leave-one-corridor-out:** the High-minus-Low gap recomputed after dropping each SA3 in turn.

# %%
def rho_grid(chg_df: pd.DataFrame, elig_df: pd.DataFrame) -> pd.DataFrame:
    """Spearman ρ between each exposure variant and the change, for every segment × window."""
    ex = elig_df.set_index("poa")
    exp_cols = {k: (ex[v] * (-1 if v == "E3_dist_major_km" else 1)) for k, v in EXPOSURE_VARIANTS.items()}
    out = {}
    for seg in SEGS:
        for tr in TRANS:
            d = chg_df[(chg_df.seg == seg) & (chg_df.trans == tr)].set_index("poa")
            out[(seg, tr)] = {k: stats.spearmanr(e.loc[d.index], d.chg).statistic for k, e in exp_cols.items()}
    return pd.DataFrame(out)

grid = rho_grid(chg, elig)
fig, ax = plt.subplots(figsize=(13, 3.8))
sns.heatmap(grid, annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-0.6, vmax=0.6, ax=ax, cbar_kws={"label": "Spearman ρ"})
ax.set_title("Association between exposure and rent change under each exposure definition")
ax.set_xlabel("segment, window"); ax.set_ylabel("")
plt.tight_layout()
plt.show()

# %%
PRIMARY_EXPOSURE = "E2 λ=3 km (primary)"

def agreement_share(g: pd.DataFrame, cells: list, thr: float = 0.10) -> float:
    """Share of alternative exposure definitions whose ρ has the same sign as the primary one (|ρ| ≥ thr), averaged over cells."""
    shares = []
    for c in cells:
        p = g.loc[PRIMARY_EXPOSURE, c]
        if abs(p) < thr:
            continue
        others = g[c].drop(PRIMARY_EXPOSURE)
        shares.append(((np.sign(others) == np.sign(p)) & (others.abs() >= thr)).mean())
    return float(np.mean(shares)) if shares else np.nan

primary_cells = [("f01", t) for t in PRIMARY_WINDOWS]
agree_primary = agreement_share(grid, primary_cells)
agree_all = agreement_share(grid, list(grid.columns))

def loo_stability(chg_df: pd.DataFrame, seg: str = "f01") -> tuple[float, pd.DataFrame]:
    """Share of (window, dropped corridor) runs where the High−Low gap keeps its full-sample sign."""
    rows = []
    for tr in PRIMARY_WINDOWS:
        d = chg_df[(chg_df.seg == seg) & (chg_df.trans == tr)]
        full = tier_gap_arrays(d.chg.to_numpy(), d.tier.astype(str).to_numpy())
        for sa3 in d.sa3.unique():
            dd = d[d.sa3 != sa3]
            g = tier_gap_arrays(dd.chg.to_numpy(), dd.tier.astype(str).to_numpy())
            rows.append({"window": tr, "dropped": sa3, "gap": g, "same_sign": np.sign(g) == np.sign(full) if np.isfinite(g) else np.nan})
    out = pd.DataFrame(rows)
    return float(out.same_sign.dropna().astype(float).mean()), out

loo_share, loo_tbl = loo_stability(chg)
print(f"Agreement of alternative exposure definitions (primary cells): {agree_primary:.0%} | all 10 cells: {agree_all:.0%}")
print(f"Leave-one-corridor-out sign stability (f01, T1–T3): {loo_share:.0%} of {loo_tbl.same_sign.notna().sum()} runs")

# %% [markdown]
# ## 6.5 Evidence grade and finding for RQ3

# %%
def grade_evidence(res_df: pd.DataFrame, agree: float, loo: float) -> str:
    """Apply the grading rules stated at the top of the notebook (primary segment f01, windows T1–T3)."""
    prim = res_df[(res_df.seg == "f01") & res_df.trans.isin(PRIMARY_WINDOWS)]
    n_sig = int(prim.excludes_0.sum())
    if n_sig >= 2 and agree >= 0.8 and loo >= 0.9:
        return "A"
    if n_sig >= 1 and agree >= 0.6:
        return "B"
    return "C"

GRADE = grade_evidence(res, agree_primary, loo_share)
GRADE_TEXT = {
    "A": "a stable association across windows and exposure definitions, which justifies taking the corridor results forward for investigation (still not evidence of cause)",
    "B": "a signal in at least one window that depends on the window or on how exposure is defined, so it should be reported as tentative",
    "C": "no pattern that can be distinguished from the common market trend at this resolution; this is a finding about the limits of the data, not proof that there is no effect",
}
def fmt_p(p: float) -> str:
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"

prim = res[(res.seg == "f01") & res.trans.isin(PRIMARY_WINDOWS)]
bul = "\n".join(f"- **{TRANS_LABEL[r.trans]}:** High − Low gap {r.gap_pp:+.1f} pp (90% cluster-bootstrap interval {r.gap_lo:+.1f} to {r.gap_hi:+.1f}); "
                f"Spearman ρ = {r.rho:+.2f}, naive permutation {fmt_p(r.p_perm_naive)}." for r in prim.itertuples())
n_hi, n_lo = int(prim.n_High.iloc[0]), int(prim.n_Low.iloc[0])
sc_sig = int(contrast.loc[contrast.window.isin([TRANS_LABEL[t] for t in PRIMARY_WINDOWS]), "excludes_0"].sum())

f01 = res[res.seg == "f01"].set_index("trans")
t0, t1, cm = f01.loc["T0"], f01.loc["T1"], f01.loc["CUM"]
pattern = (f"Over the whole period (2018 → plateau) the High tier's studio/1BR rents grew {abs(cm.gap_pp):.1f} pp {'less' if cm.gap_pp < 0 else 'more'} than the Low tier's "
           f"(90% interval {cm.gap_lo:+.1f} to {cm.gap_hi:+.1f}). Underneath is a dip-and-rebound: during the 2021 closure the High tier fell "
           f"{abs(t0.gap_pp):.1f} pp {'more' if t0.gap_pp < 0 else 'less'} than the Low tier, and in the recovery it rose {abs(t1.gap_pp):.1f} pp {'more' if t1.gap_pp > 0 else 'less'}.")
md(f"**Key finding – RQ3 (studio/1BR flats; {n_hi} High-tier and {n_lo} Low-tier postcodes).**\n\n{pattern}\n\n"
   f"Post-closure windows used for the grade:\n\n{bul}\n\n"
   f"- **Alternative exposure definitions:** {agree_primary:.0%} agree in sign with the primary definition (and have |ρ| ≥ 0.10).\n"
   f"- **Leave-one-corridor-out:** the sign of the gap is unchanged in {loo_share:.0%} of runs.\n"
   f"- **Small flats versus 2BR flats:** the difference between the two segments' High−Low gaps excludes zero in {sc_sig} of 3 windows.\n\n"
   f"**Evidence grade: {GRADE}.** This means {GRADE_TEXT[GRADE]}.\n\n"
   "*Caution:* a closure-then-rebound pattern is what a shock to campus-linked demand would produce, but equally what a shock to inner-city demand in "
   "general (workplaces, tourism, border-related moves) would produce. These data cannot separate the two.")

# %% [markdown]
# # 7. RQ4 – Which corridors warrant further investigation?
#
# **Research question.** Which corridors show rent growth above the Low-exposure benchmark, consistently across segments and windows, with enough bonds to trust?
#
# For each corridor (SA3) with at least 3 eligible postcodes, the median change is compared with the **median of the Low tier** in the same segment and window.
# A corridor is *consistent* when it beats the benchmark in at least 5 of the 6 comparisons (2 segments × windows T1–T3).

# %%
bench = (chg[(chg.tier == "Low")].groupby(["seg", "trans"]).chg.median().rename("bench").reset_index())
cc = chg[chg.seg.isin(SEGS) & chg.trans.isin(PRIMARY_WINDOWS)].merge(bench, on=["seg", "trans"])
cc = cc.groupby(["sa3", "seg", "trans"]).agg(med=("chg", "median"), bench=("bench", "first"), pcs=("poa", "nunique")).reset_index()
cc["above"] = cc.med > cc.bench
n_bonds = (panel[panel.seg.isin(SEGS) & panel.group.notna()].groupby("sa3").size().rename("bonds_f01_f2"))
corr_tab = (cc.groupby("sa3").agg(postcodes=("pcs", "max"), above_of_6=("above", "sum"), avg_gap_pp=("med", "mean"))
            .join(cc.assign(g=cc.med - cc.bench).groupby("sa3").g.mean().rename("avg_gap_vs_low_pp"))
            .join(elig.groupby("sa3").E2_rows_l3.mean().rename("mean_E2"))
            .join(n_bonds))
corr_tab = corr_tab[corr_tab.postcodes >= 3].drop(columns="avg_gap_pp")
E2_EXPOSED = elig.loc[elig.tier == "High", "E2_rows_l3"].min()          # lower bound of the High tier
corr_tab["exposed"] = corr_tab.mean_E2 >= E2_EXPOSED
corr_tab["consistent"] = (corr_tab.above_of_6 >= 5) & (corr_tab.bonds_f01_f2 >= 2000)
corr_tab["candidate"] = corr_tab.consistent & corr_tab.exposed
corr_tab = corr_tab.sort_values(["above_of_6", "avg_gap_vs_low_pp"], ascending=False)
corr_tab.round(1)

# %%
fig, ax = plt.subplots(figsize=(9.5, 5.4))
colors = np.select([corr_tab.candidate, corr_tab.consistent], ["#c0392b", "#e59866"], default="#aab7b8")
ax.barh(corr_tab.index, corr_tab.avg_gap_vs_low_pp, color=colors)
ax.axvline(0, color="black", lw=0.8); ax.invert_yaxis()
ax.set_xlabel("Average gap versus the Low-exposure benchmark (pp)")
ax.set_title("Corridors versus the Low benchmark")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color="#c0392b", label="consistent and high-exposure"), Patch(color="#e59866", label="consistent but low-exposure"),
                   Patch(color="#aab7b8", label="not consistent (<5 of 6)")], frameon=False, loc="lower right")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 7.1 Finding for RQ4

# %%
flagged = corr_tab[corr_tab.candidate].index.tolist()
exposed_names = corr_tab[corr_tab.exposed].index.tolist()
low_consistent = corr_tab[corr_tab.consistent & ~corr_tab.exposed]
if flagged and GRADE in ("A", "B"):
    head = f"With evidence grade {GRADE}, the high-exposure corridors that consistently beat the Low benchmark are candidates for deeper investigation: **{', '.join(flagged)}**."
elif flagged:
    head = f"The grade is C, so this is a descriptive ranking only. High-exposure corridors that beat the Low benchmark in at least 5 of 6 comparisons: **{', '.join(flagged)}**."
else:
    others = "; ".join(f"{n} (mean E2 {low_consistent.loc[n, 'mean_E2']:.1f})" for n in low_consistent.index) or "none"
    head = (f"None of the {len(exposed_names)} high-exposure corridors ({', '.join(exposed_names)}) beat the Low-exposure benchmark in at least 5 of 6 comparisons. "
            f"The corridors that did are low-exposure ones: {others}. Fast rent growth is therefore not specific to campus areas.")
md("**Key finding – RQ4.** " + head + " Corridors are ranked by how rents moved relative to low-exposure flat markets; the ranking says nothing about why.")

# %% [markdown]
# # 8. Robustness
#
# Beyond the grid and leave-one-out checks above, three further choices could change the picture: the minimum bonds per cell, how the tiers are drawn,
# and whether the City of Sydney's own postcodes drive the result.

# %%
def primary_summary(chg_df: pd.DataFrame, elig_df: pd.DataFrame, label: str) -> dict:
    """Median High−Low gap and ρ for studio/1BR across the post-closure windows, for a given set of data."""
    out = {"scenario": label}
    gaps, rhos = [], []
    for tr in PRIMARY_WINDOWS:
        d = chg_df[(chg_df.seg == "f01") & (chg_df.trans == tr)]
        gaps.append(tier_gap_arrays(d.chg.to_numpy(), d.tier.astype(str).to_numpy()))
        rhos.append(stats.spearmanr(d.E2_rows_l3, d.chg).statistic if len(d) > 10 else np.nan)
    for tr, g, r in zip(PRIMARY_WINDOWS, gaps, rhos):
        out[f"gap {tr}"] = g; out[f"ρ {tr}"] = r
    out["postcodes (T1)"] = len(chg_df[(chg_df.seg == "f01") & (chg_df.trans == "T1")])
    return out

scen = []
for mn in (30, 60, 100):                                     # (a) minimum bonds per cell
    c = build_changes(cell_pd, mn).merge(elig[["poa", "sa3", "tier", "E2_rows_l3", "city_of_sydney"]], on="poa")
    scen.append(primary_summary(c, elig, f"min {mn} bonds per cell"))
c_nocos = chg[~chg.city_of_sydney]                            # (b) without the City of Sydney's own postcodes
scen.append(primary_summary(c_nocos, elig, "excluding City of Sydney postcodes"))
e4 = elig.copy(); q = e4.E2_rows_l3.quantile([0.25, 0.75])    # (c) quartile tiers instead of terciles
e4["tier"] = np.select([e4.E2_rows_l3 <= q.iloc[0], e4.E2_rows_l3 >= q.iloc[1]], ["Low", "High"], default="Mid")
c_q = chg.drop(columns="tier").merge(e4[["poa", "tier"]], on="poa")
scen.append(primary_summary(c_q, e4, "top vs bottom quartile tiers"))
pd.DataFrame(scen).round(2)

# %% [markdown]
# **How much can the robustness checks prove?** The exposure variants (λ values, equal-split weights, distance, SA4 share) all derive from the same
# campus locations, which is why they agree so closely. Agreement across them shows the result does not hinge on a tuning choice, but it does
# **not** test the underlying assumption that proximity to a campus is a good proxy for where students rent.

# %% [markdown]
# # 9. Context: other explanations
#
# Rent differences between areas can have other sources. Three descriptive checks look at housing supply, short- and mid-term stays, and baseline market structure.
# They do not adjust the results above.
#
# ## 9.1 Residential development applications (supply proposals)

# %%
DA_PATH = PROC / "da_residential_2022_2026.parquet"
if DA_PATH.exists():
    da = pd.read_parquet(DA_PATH)
    da["poa"] = da.postcode.astype(str).str.zfill(4)
    da = da[da.poa.isin(elig.poa)].copy()
    da["year"] = da.lodged.dt.year
    flat_types = "Residential flat building|Multi-dwelling housing|Shop top housing|Co-living|Boarding house|Attached dwelling|Semi-detached"
    da["flat_type"] = da.dev_types.str.contains(flat_types, case=False, na=False)
    da["month"] = da.lodged.dt.to_period("M")
    months_cov = da.month.nunique()
    print(f"Residential DAs in eligible postcodes: {len(da):,} | sampled months: {months_cov} ({', '.join(str(m) for m in sorted(da.month.unique()))})")
    print(f"Share of DAs with a dwelling count: {da.dwellings.notna().mean():.0%}")
    per_pc = (da.groupby("poa").agg(das=("pan", "size"), dwellings=("dwellings", "sum")).reset_index()
              .merge(elig[["poa", "group", "tier"]], on="poa", how="right").fillna({"das": 0, "dwellings": 0}))
    per_pc["DAs per year"] = per_pc.das / months_cov * 12                # annualised from the sampled months
    per_pc["proposed dwellings per year"] = per_pc.dwellings / months_cov * 12
    da_summary = (per_pc.groupby("group").agg(postcodes=("poa", "size"), median_DAs_per_year=("DAs per year", "median"),
                                              median_dwellings_per_year=("proposed dwellings per year", "median")).reindex(list(COLORS)))
    display(da_summary)
    DA_NOTE = (f"Rates are annualised from {months_cov} sampled months (January and July of each year) and describe proposals: many applications are never built, "
               "so the table shows where supply is being proposed, not where it was delivered.")
else:
    print("DA history not found (run scripts/07_pull_da.py to generate it); this subsection is skipped.")
    DA_NOTE = ""
print(DA_NOTE)

# %% [markdown]
# ## 9.2 Airbnb listings by postcode (snapshot)
#
# Listing points are assigned to postcode polygons with a spatial join (`sjoin`). The file is a single snapshot (17 Sep 2026): it shows today's
# stock, not the history of listings switching to or from long-term renting.

# %%
air_path = AIRBNB_DIR / "listings.csv.gz"
if air_path.exists():
    air = pd.read_csv(air_path, usecols=["id", "latitude", "longitude", "room_type", "minimum_nights", "last_scraped"], low_memory=False)
    pts = gpd.GeoDataFrame(air, geometry=gpd.points_from_xy(air.longitude, air.latitude), crs=4326).to_crs(poa_gdf.crs)
    air_poa = gpd.sjoin(pts, poa_gdf[["poa", "geometry"]], how="inner", predicate="within")
    air_poa["mid_term"] = air_poa.minimum_nights >= 28
    air_pc = air_poa.groupby("poa").agg(listings=("id", "size"), mid_term=("mid_term", "sum")).reset_index()
    air_pc = elig[["poa", "group"]].merge(air_pc, on="poa", how="left").fillna({"listings": 0, "mid_term": 0})
    air_summary = (air_pc.groupby("group").agg(postcodes=("poa", "size"), median_listings=("listings", "median"),
                                               median_mid_term=("mid_term", "median"), total_mid_term=("mid_term", "sum")).reindex(list(COLORS)))
    print(f"Listings: {len(air):,} | matched to an eligible-pool postcode polygon: {len(air_poa):,} | snapshot: {air.last_scraped.iloc[0]}")
    display(air_summary)
else:
    print("Inside Airbnb file not found; subsection skipped.")

# %% [markdown]
# ## 9.3 Market structure at baseline
#
# High-exposure postcodes are also more flat-dominated and dearer in 2018, which is why changes (not levels) are compared. The table checks whether the
# comparison tiers look alike on those dimensions.

# %%
bal = (elig.groupby("tier", observed=True)
       .agg(postcodes=("poa", "size"), flat_share_2018=("flat_share_2018", "median"), med_f01_2018=("med_f01_2018", "median"),
            med_f2_2018=("med_f2_2018", "median"), median_dist_km=("E3_dist_major_km", "median"), city_of_sydney=("city_of_sydney", "sum")))
bal

# %% [markdown]
# # 10. Overall findings, recommendations and limitations
#
# ## 10.1 Overall findings

# %%
n_pos = int((corr.median_chg_f01 > 0).sum())
corridor_line = (f"High-exposure corridors that consistently beat the Low benchmark: {', '.join(flagged)}." if flagged
                 else "No high-exposure corridor consistently beat the Low-exposure benchmark, so the corridor ranking does not point to campus areas as a group.")
md(f"""
1. **A shared cycle dominates.** New-lease rents for flats fell during the 2021 closure and then rose strongly everywhere (RQ1). Differences between exposure groups in the cumulative change are small relative to this common movement.
2. **Growth was widespread.** Cumulative studio/1BR rent change from 2018 to the plateau-and-decline phase was positive in {n_pos} of {len(corr)} corridors (RQ2).
3. **Association with campus exposure: evidence grade {GRADE}.** {pattern} (RQ3)
4. **Seasonality.** {SEASON_TEXT}
5. **Corridors.** {corridor_line} (RQ4)
""")

# %% [markdown]
# ## 10.2 Recommendations for the City of Sydney
#
# The wording below follows the evidence grade computed above.

# %%
if GRADE == "A" and flagged:
    recs = [f"Prioritise the flagged corridors ({', '.join(flagged)}) for deeper investigation, for example by asking education providers and student-accommodation operators for occupancy and waiting-list data.",
            "Describe the finding in briefings as a **stable association**, not a cause."]
elif GRADE in ("A", "B"):
    recs = ["Treat the pattern as tentative. It rests mainly on the rebound after the 2021 closure, which campus-linked and general inner-city demand shocks would both produce.",
            "Test the February seasonal lead directly: ask student-accommodation operators and education providers for lease-start dates and term-address counts by suburb.",
            "Do not use these results to rank corridors for student-related action; no high-exposure corridor consistently beat the low-exposure benchmark."]
else:
    recs = ["Do not use these results to rank corridors for student-related action; the data cannot separate campus exposure from the common cycle at postcode resolution.",
            "Ask for the data that would sharpen the question: student numbers or term addresses by suburb, occupancy and rents in purpose-built student accommodation, and weekly rather than period-median rent series.",
            "Use the descriptive results (RQ1–RQ2) for context: new-lease flat rents recovered from the 2021 trough and now sit well above 2018 in every corridor."]
recs.append("Keep the 2019–2020 gap in view: without pre-COVID years beyond 2018, the analysis cannot test whether high-exposure areas were already on different trends.")
md("\n".join(f"{i}. {r}" for i, r in enumerate(recs, 1)))

# %% [markdown]
# ## 10.3 Limitations
#
# - **Exposure is modelled, not observed.** Campus weights are an allocation of SA4 enrolments by CRICOS course-location rows; the Department of Education file records place of study (not residence) for a single year (2025).
# - **Coarse geography.** Rent is known only by postcode, and distances use postcode-area centroids (about 1 km resolution). UNSW and Macquarie were mapped to neighbouring postcodes because ABS has no postcode area for their institutional postcodes.
# - **New leases only.** Bond lodgements capture rents at the start of a tenancy. They say nothing about rents paid by existing tenants, and do not identify tenants (students or otherwise).
# - **Observational data.** Neighbouring postcodes share conditions, the exposure variants derive from the same campuses, and the grade rules are descriptive. Nothing here establishes cause.
# - **Time coverage.** 2019–2020 is missing; the 2018 file comes from a data.nsw mirror whose provenance should be confirmed. Phases are defined from visas granted, which are a flow, not the number of students present.
# - **Context data are partial.** DAs are proposals and often lack dwelling counts; Airbnb is a single snapshot.
# - **Median-based phase comparisons** blend a phase's within-period movement into its level; phases of different lengths are therefore only roughly comparable.
#
# ## 10.4 Conclusion
#
# This analysis examined whether new-lease rents in Sydney's flat market differ by proximity to higher-education campuses. Rents moved together through a
# common cycle, and the extent to which campus exposure adds to that cycle is summarised by the evidence grade above. The result is intentionally calibrated:
# it tells the Council where to look and how firmly to say it, and where the available data stop being able to answer.
#
# ## 10.5 Future development
# - Add monthly counts of students in Australia (Department of Education) to replace visa grants as the phase indicator.
# - Obtain pre-COVID bond files for 2019–2020 to test for pre-existing trends.
# - Geocode campuses and use the postcode-level 2026 Census to normalise by renter households.
# - Request purpose-built student accommodation occupancy and rents from operators.
#
# ---
# *Reproducibility: all inputs are in `data/raw/`, derived tables in `data/processed/`, and the build scripts in `data/scripts/` (run in numerical order).*
