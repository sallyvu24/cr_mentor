"""Decisions 3 and 4 - what does the Census exposure (E4) measure, and would G33 add an independent student signal?"""
import numpy as np, pandas as pd
from scipy import stats
from _common import DATA, PROC

cen = pd.read_csv(PROC / "census2021_poa_features.csv", dtype={"poa": str})
pool = cen[cen.city_of_sydney | cen.comparator_candidate].copy()
pool["tier_E2"] = pd.qcut(pool.E2_rows_l3, 3, labels=["Low", "Mid", "High"])
pool["tier_E4"] = pd.qcut(pool.uni_per_100, 3, labels=["Low", "Mid", "High"])
rho = lambda a, b: round(stats.spearmanr(a, b, nan_policy="omit").statistic, 2)
print(f"[1] Spearman E2 vs E4: pool {rho(pool.E2_rows_l3, pool.uni_per_100)} | all 247 {rho(cen.E2_rows_l3, cen.uni_per_100)}")
print(f"    E4 vs renter share {rho(pool.uni_per_100, pool.renter_share)} | E2 vs renter share {rho(pool.E2_rows_l3, pool.renter_share)}")
print(f"    E4 (uni per 100) vs full-time 15-24 variant: {rho(pool.uni_per_100, pool.uni_ft1524_per_100)}")
print("\n[2] Tier cross-tab (rows E2, cols E4); same-tier share =", round((pool.tier_E2 == pool.tier_E4).mean(), 2))
print(pd.crosstab(pool.tier_E2, pool.tier_E4))
print("\n[3] Tier profiles (medians)")
for t in ("tier_E2", "tier_E4"):
    print(t); print(pool.groupby(t, observed=True)[["uni_per_100", "renter_share", "Median_rent_weekly", "Median_tot_hhd_inc_weekly"]].median().round(1))
print("\nCity of Sydney postcodes in E4 tiers:", pool[pool.city_of_sydney].tier_E4.value_counts().to_dict())

g33 = pd.read_csv(DATA / "raw/abs_census/extracted/2021 Census GCP Postal Areas for NSW/2021Census_G33_NSW_POA.csv", dtype={"POA_CODE_2021": str})
g33["poa"] = g33.POA_CODE_2021.str[-4:]
g33["nonfam_share"] = g33.Tot_Non_family_households / g33.Tot_Tot
x = pool.merge(g33[["poa", "nonfam_share"]], on="poa")
print(f"\n[4] G33 non-family-household share vs E4 {rho(x.nonfam_share, x.uni_per_100)} | vs renter share {rho(x.nonfam_share, x.renter_share)} | vs E2 {rho(x.nonfam_share, x.E2_rows_l3)}")
