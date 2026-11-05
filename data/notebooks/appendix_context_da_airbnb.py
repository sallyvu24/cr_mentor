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
# # Appendix: development applications and Airbnb as context
# ### Companion to `sydney_student_rent_eda.ipynb` (section 9.3)
#
# Housing supply and short-term letting are two obvious alternative explanations for rent differences between areas. This appendix keeps the
# descriptive checks that were in section 9 of the main notebook before the data decisions of November 2026 (decision 6: neither source changes a
# finding, so they were moved here rather than deleted). Neither table enters any test or grade.
#
# - **Residential development applications (NSW Planning Portal):** proposals, sampled in January and July of each year, 2022–2026.
# - **Inside Airbnb, Sydney:** one snapshot of listings (17 September 2026).
#
# The comparison groups are the same as in the main notebook: City of Sydney postcodes, and flat-heavy comparator postcodes split into E2 tertiles.

# %%
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import geopandas as gpd
from IPython.display import Markdown, display

warnings.filterwarnings("ignore", category=FutureWarning)
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "processed").exists())
PROC, RAW = ROOT / "processed", ROOT / "raw"
AIRBNB_DIR = ROOT.parent / "inside_airbnb_data"
pd.set_option("display.float_format", lambda v: f"{v:,.2f}")
COLORS = ["City of Sydney", "Comparator – High", "Comparator – Mid", "Comparator – Low"]

def md(text: str) -> None:
    display(Markdown(text))

# Comparison groups, built exactly as in section 3.5 of the main notebook
base = pd.read_csv(PROC / "postcode_baseline.csv", dtype={"poa": str, "E3_nearest_major_poa": str})
elig = base[base.city_of_sydney | base.comparator_candidate].copy()
elig["tier"] = pd.qcut(elig.E2_rows_l3, 3, labels=["Low", "Mid", "High"])
elig["group"] = np.where(elig.city_of_sydney, "City of Sydney", "Comparator – " + elig.tier.astype(str))
print(f"Eligible postcodes: {len(elig)} |", elig.group.value_counts().reindex(COLORS).to_dict())

# %% [markdown]
# ## A.1 Residential development applications (supply proposals)

# %%
DA_PATH = PROC / "da_residential_2022_2026.parquet"
da = pd.read_parquet(DA_PATH)
da["poa"] = da.postcode.astype(str).str.zfill(4)
da = da[da.poa.isin(elig.poa)].copy()
flat_types = "Residential flat building|Multi-dwelling housing|Shop top housing|Co-living|Boarding house|Attached dwelling|Semi-detached"
da["flat_type"] = da.dev_types.str.contains(flat_types, case=False, na=False)
da["month"] = da.lodged.dt.to_period("M")
months_cov = da.month.nunique()
print(f"Residential DAs in eligible postcodes: {len(da):,} | sampled months: {months_cov} ({', '.join(str(m) for m in sorted(da.month.unique()))})")
print(f"Dwelling count recorded: {da.dwellings.notna().mean():.1%} of DAs | of which zero proposed dwellings: {(da.dwellings == 0).mean():.1%} "
      f"(alterations, fences, pools and similar works)")
per_pc = (da.groupby("poa").agg(das=("pan", "size"), dwellings=("dwellings", "sum")).reset_index()
          .merge(elig[["poa", "group", "tier"]], on="poa", how="right").fillna({"das": 0, "dwellings": 0}))
per_pc["DAs per year"] = per_pc.das / months_cov * 12                # annualised from the sampled months
per_pc["proposed dwellings per year"] = per_pc.dwellings / months_cov * 12
da_summary = (per_pc.groupby("group").agg(postcodes=("poa", "size"), median_DAs_per_year=("DAs per year", "median"),
                                          median_dwellings_per_year=("proposed dwellings per year", "median")).reindex(COLORS))
da_summary

# %%
tiers = ["Comparator – Low", "Comparator – Mid", "Comparator – High"]
def trend(col: str) -> str:
    s = da_summary.loc[tiers, col]
    return "rises" if s.is_monotonic_increasing and s.iloc[-1] > s.iloc[0] else "falls" if s.is_monotonic_decreasing and s.iloc[-1] < s.iloc[0] else "does not move steadily"
md(f"Rates are annualised from {months_cov} sampled months (January and July of each year) and describe **proposals**: many applications are never built, "
   f"and {(da.dwellings == 0).mean():.0%} of them propose no new dwelling at all. From the Low to the High comparator tier, the median number of DAs a year "
   f"{trend('median_DAs_per_year')} ({', '.join(f'{v:.0f}' for v in da_summary.loc[tiers, 'median_DAs_per_year'])}) and the median number of proposed dwellings "
   f"{trend('median_dwellings_per_year')} ({', '.join(f'{v:.0f}' for v in da_summary.loc[tiers, 'median_dwellings_per_year'])}); the City of Sydney has the lowest "
   f"rates ({da_summary.loc['City of Sydney', 'median_DAs_per_year']:.0f} DAs, {da_summary.loc['City of Sydney', 'median_dwellings_per_year']:.0f} dwellings). "
   "Differences of this size in proposals, from ten sampled months and without completions data, cannot be used to adjust the rent comparison.")

# %% [markdown]
# ## A.2 Airbnb listings by postcode (snapshot)
#
# Listing points are assigned to postcode polygons with a spatial join (`sjoin`). The file is a single snapshot, so it shows today's stock, not the
# history of homes switching to or from long-term renting.

# %%
POA_SHP = RAW / "abs_poa" / "shp" / "POA_2021_AUST_GDA2020.shp"
poa_gdf = gpd.read_file(POA_SHP, bbox=(150.55, -34.25, 151.45, -33.35)).rename(columns={"POA_CODE21": "poa"})[["poa", "geometry"]]
air = pd.read_csv(AIRBNB_DIR / "listings.csv.gz", usecols=["id", "latitude", "longitude", "room_type", "minimum_nights", "last_scraped"], low_memory=False)
pts = gpd.GeoDataFrame(air, geometry=gpd.points_from_xy(air.longitude, air.latitude), crs=4326).to_crs(poa_gdf.crs)
air_poa = gpd.sjoin(pts, poa_gdf[poa_gdf.poa.isin(elig.poa)][["poa", "geometry"]], how="inner", predicate="within")
air_poa["mid_term"] = air_poa.minimum_nights >= 28
air_pc = air_poa.groupby("poa").agg(listings=("id", "size"), mid_term=("mid_term", "sum")).reset_index()
air_pc = elig[["poa", "group"]].merge(air_pc, on="poa", how="left").fillna({"listings": 0, "mid_term": 0})
air_summary = (air_pc.groupby("group").agg(postcodes=("poa", "size"), median_listings=("listings", "median"),
                                           median_mid_term=("mid_term", "median"), total_mid_term=("mid_term", "sum")).reindex(COLORS))
print(f"Listings: {len(air):,} | inside an eligible-pool postcode polygon: {len(air_poa):,} | snapshot: {air.last_scraped.iloc[0]}")
air_summary

# %%
falls = air_summary.loc[COLORS, "median_listings"].is_monotonic_decreasing
md(f"Median listings per postcode: {', '.join(f'{g} {v:.0f}' for g, v in air_summary.median_listings.items())}. "
   + ("Listings are densest in the City of Sydney and fall with exposure tier, so short-term letting is concentrated where exposure is high. " if falls else "")
   + f"But the data are one snapshot ({air.last_scraped.iloc[0]}), while the rent changes being compared run from 2021 to 2026: there is no way to tell whether "
   "listings grew, shrank or moved over that period, so they cannot explain, or be used to adjust, a change in rents.")

# %% [markdown]
# ## A.3 What this means for the main notebook
#
# Both checks answer "we looked" rather than "we tested". The main notebook therefore lists supply and short-term letting among the explanations its
# data cannot test (section 9.3) and does not adjust any result for them.
