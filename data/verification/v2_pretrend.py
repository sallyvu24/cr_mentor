"""Decision 2 - pre-COVID parallel-trend test with DCJ medians (flat/unit, 1BR and 2BR), High vs Low E2 tier.
Shows how sensitive the 'parallel before COVID' statement is to the way a year is aggregated."""
import numpy as np, pandas as pd
from _common import PROC, load_pool, cluster_ci

elig = load_pool()
dcj = pd.read_parquet(PROC / "dcj_rent_postcode_2018_2022.parquet")
d = (dcj[(dcj.dwelling == "Flat/Unit") & dcj.bedrooms.isin(["1 Bedroom", "2 Bedrooms"])]
     .rename(columns={"postcode": "poa", "bedrooms": "bed"}).merge(elig[["poa", "sa3", "tier"]], on="poa").dropna(subset=["med"]))
d["lm"] = np.log(d.med) * 100
d["yr"], d["q"] = d.quarter.dt.year, d.quarter.dt.quarter

AGG = {"annual mean": lambda x, y: x[x.yr == y].groupby("poa").med.mean(),
       "annual median": lambda x, y: x[x.yr == y].groupby("poa").med.median(),
       "Q4 only": lambda x, y: x[(x.yr == y) & (x.q == 4)].set_index("poa").med}
print("[A] High-minus-Low gap in annual rent growth (pp). Documented 1BR: -0.3 | -9.6 | -0.6 | +6.8")
for bed in ["1 Bedroom", "2 Bedrooms"]:
    x = d[d.bed == bed]
    for name, f in AGG.items():
        row = []
        for a in (2018, 2019, 2020, 2021):
            ch = (100 * np.log(f(x, a + 1) / f(x, a))).dropna().rename("chg").reset_index().merge(elig[["poa", "sa3", "tier"]], on="poa")
            g = ch[ch.tier == "High"].chg.median() - ch[ch.tier == "Low"].chg.median()
            row.append(round(g, 1))
        print(f"  {bed:11s} {name:14s} {row}")

print("\n[B] Quarterly High-minus-Low gap, index 2019Q4 = 0 (pp)")
for bed in ["1 Bedroom", "2 Bedrooms"]:
    p = d[d.bed == bed].pivot_table(index="poa", columns="quarter", values="lm")
    p = p.sub(p[pd.Period("2019Q4")], axis=0)
    t = elig.set_index("poa").tier.reindex(p.index)
    gap = p[t == "High"].median() - p[t == "Low"].median()
    print(bed, gap.round(1).to_dict())

print("\n[C] Pre-COVID slope 2018Q1-2019Q4 (pp per year), High minus Low, 90% cluster-bootstrap interval")
for bed in ["1 Bedroom", "2 Bedrooms"]:
    x = d[(d.bed == bed) & (d.quarter <= pd.Period("2019Q4"))].copy()
    x["t"] = (x.yr - 2018) + (x.q - 1) / 4
    sl = (x.groupby("poa").apply(lambda g: np.polyfit(g.t, g.lm, 1)[0] if g.t.nunique() >= 6 else np.nan)
          .rename("chg").dropna().reset_index().merge(elig[["poa", "sa3", "tier"]], on="poa"))
    lo, hi = cluster_ci(sl)
    print(f"  {bed}: gap {sl[sl.tier=='High'].chg.median() - sl[sl.tier=='Low'].chg.median():+.2f}  90% CI [{lo:+.2f}, {hi:+.2f}]")
