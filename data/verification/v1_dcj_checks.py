"""Decision 2 - is DCJ usable? (a) agreement with our own bond medians, (b) how much of f01 is a studio ('Bedsitter' proxy),
(c) which postcodes lose cells to suppression (<=10 bonds)."""
import numpy as np, pandas as pd
from _common import PROC, load_pool

elig = load_pool()
dcj = pd.read_parquet(PROC / "dcj_rent_postcode_2018_2022.parquet")
panel = pd.read_parquet(PROC / "analysis_bond_panel.parquet", columns=["date", "poa", "dwelling", "bedrooms", "rent", "seg"])

f = panel[(panel.seg == "f01") & panel.poa.isin(elig.poa)].merge(elig[["poa", "tier"]], on="poa")
f["yr"] = f.date.dt.year
print("[1] Share of f01 bonds that are studios (bedrooms == 0), by tier and year")
print(f.assign(studio=f.bedrooms == 0).groupby(["tier", "yr"]).studio.mean().unstack().round(2))

mine = (panel[(panel.dwelling == "F") & panel.bedrooms.isin([1, 2]) & panel.rent.notna()]
        .assign(quarter=lambda d: d.date.dt.to_period("Q"), bed=lambda d: d.bedrooms.map({1: "1 Bedroom", 2: "2 Bedrooms"}))
        .groupby(["poa", "quarter", "bed"]).rent.agg(own_med="median", own_n="size").reset_index())
d = dcj[(dcj.dwelling == "Flat/Unit") & dcj.bedrooms.isin(["1 Bedroom", "2 Bedrooms"])].rename(columns={"postcode": "poa", "bedrooms": "bed"})
m = d.merge(mine, on=["poa", "quarter", "bed"]).dropna(subset=["med", "own_med"])
m = m[m.poa.isin(elig.poa)].assign(diff=lambda x: x.own_med - x.med, yr=lambda x: x.quarter.dt.year)
print("\n[2] DCJ vs own bond medians, by year")
print(m.groupby("yr").apply(lambda x: pd.Series({"cells": len(x), "corr": np.corrcoef(x.own_med, x.med)[0, 1],
      "identical %": (x["diff"] == 0).mean() * 100, "within $10 %": (x["diff"].abs() <= 10).mean() * 100})).round(3))

d1 = d.merge(elig[["poa", "tier"]], on="poa")
d1 = d1[d1.quarter.dt.year.between(2018, 2022)]
print("\n[3] Share of postcode-quarters with a published (non-suppressed) median")
print(d1.assign(ok=d1.med.notna(), yr=d1.quarter.dt.year).groupby(["bed", "tier", "yr"]).ok.mean().unstack().round(2))
