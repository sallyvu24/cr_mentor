"""Decision 1 - does the evidence grade change if phases come from students PRESENT (BP0019) instead of visas GRANTED (BP0015)?
Re-implements the main notebook's grading inputs (section 6.4-6.5) for either phase scheme, small flats (f01), E2 tiers."""
import numpy as np, pandas as pd
from scipy import stats
from _common import PROC, load_pool, cluster_ci

elig = load_pool()
full = pd.read_csv(PROC / "postcode_baseline.csv", dtype={"poa": str}).set_index("poa")
panel = pd.read_parquet(PROC / "analysis_bond_panel.parquet", columns=["date", "poa", "seg", "rent"])
panel = panel[(panel.seg == "f01") & panel.poa.isin(elig.poa)]
SCHEMES = {
    "flow (BP0015)":  [("b", "2018-01-01", "2018-12-31"), ("c", "2021-01-01", "2021-11-30"), ("r", "2021-12-01", "2023-07-31"), ("k", "2023-08-01", "2024-06-30"), ("d", "2024-07-01", "2026-09-30")],
    "stock (BP0019)": [("b", "2018-01-01", "2018-12-31"), ("c", "2021-01-01", "2021-12-31"), ("r", "2022-01-01", "2023-12-31"), ("k", "2024-01-01", "2025-06-30"), ("d", "2025-07-01", "2026-09-30")]}
WIN = {"T1": ("c", "r"), "T2": ("r", "k"), "T3": ("k", "d")}
VARIANTS = {"E2 l=1.5": "E2_rows_l1.5", "E2 l=3 (primary)": "E2_rows_l3", "E2 l=5": "E2_rows_l5", "E2 equal l=3": "E2_equal_l3", "E3 distance (inv.)": "E3_dist_major_km", "E1 SA4 share": "E1_share_he"}
PRIMARY = "E2 l=3 (primary)"

def changes(scheme):
    d = panel.copy(); d["ph"] = ""
    for n, a, b in SCHEMES[scheme]:
        d.loc[(d.date >= a) & (d.date <= b), "ph"] = n
    c = d[d.ph != ""].groupby(["poa", "ph"]).rent.agg(["median", "size"]).reset_index()
    med, n = c.pivot(index="poa", columns="ph", values="median"), c.pivot(index="poa", columns="ph", values="size")
    out = {}
    for w, (a, b) in WIN.items():
        out[w] = (100 * np.log(med[b] / med[a])).where((n[a] >= 30) & (n[b] >= 30)).dropna().rename("chg").reset_index().merge(elig[["poa", "sa3", "tier"]], on="poa")
    return out

for scheme in SCHEMES:
    ch = changes(scheme); sig = 0; rho = {}
    for w, x in ch.items():
        lo, hi = cluster_ci(x, n_boot=2000); sig += int(lo > 0 or hi < 0)
        rho[w] = {k: stats.spearmanr(full.loc[x.poa, v] * (-1 if v == "E3_dist_major_km" else 1), x.chg).statistic for k, v in VARIANTS.items()}
    g = pd.DataFrame(rho)
    shares = []
    for w in g.columns:
        p = g.loc[PRIMARY, w]
        if abs(p) < 0.10: continue
        o = g[w].drop(PRIMARY); shares.append(((np.sign(o) == np.sign(p)) & (o.abs() >= 0.10)).mean())
    agree = float(np.mean(shares))
    loo = []
    for w, x in ch.items():
        full_gap = x[x.tier == "High"].chg.median() - x[x.tier == "Low"].chg.median()
        for s in x.sa3.unique():
            y = x[x.sa3 != s]; gp = y[y.tier == "High"].chg.median() - y[y.tier == "Low"].chg.median()
            loo.append(np.sign(gp) == np.sign(full_gap))
    loo = float(np.mean(loo))
    grade = "A" if (sig >= 2 and agree >= .8 and loo >= .9) else "B" if (sig >= 1 and agree >= .6) else "C"
    print(f"{scheme:15s} windows excluding 0: {sig}/3 | exposure-definition agreement: {agree:.0%} | leave-one-corridor-out: {loo:.0%} | GRADE {grade}")
    print(g.round(2).to_string(), "\n")
