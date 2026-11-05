"""Checks on the UPDATED main notebook (BP0019 primary phases; E2 and E4 tiers). Re-tests the argument gaps that the revision did not close:
[1] RQ4 rule vs chance, [2] baseline balance and the T1 result, [3] clusters carrying the High tier under E2 and E4,
[4] a flat-minus-house contrast (uses the notebook's own placebo to ask what is specific to flats)."""
import numpy as np, pandas as pd
from scipy import stats
from _common import PROC, load_pool, cluster_ci

rng = np.random.default_rng(42)
base = pd.read_csv(PROC / "postcode_baseline.csv", dtype={"poa": str}).set_index("poa")
cen = pd.read_csv(PROC / "census2021_poa_features.csv", dtype={"poa": str}).set_index("poa")
elig = load_pool().set_index("poa")
elig["uni"] = cen.loc[elig.index, "uni_per_100"]
elig["tier_E4"] = pd.qcut(elig.uni, 3, labels=["Low", "Mid", "High"]).astype(str)
elig = elig.reset_index()
PH = {"0_base2018": ("2018-01-01", "2018-12-31"), "1_closure": ("2021-01-01", "2021-12-31"), "2_recovery": ("2022-01-01", "2023-12-31"),
      "3_plateau": ("2024-01-01", "2025-06-30"), "4_decline": ("2025-07-01", "2026-09-30")}
TR = {"T0": ("0_base2018", "1_closure"), "T1": ("1_closure", "2_recovery"), "T2": ("2_recovery", "3_plateau"), "T3": ("3_plateau", "4_decline"), "CUM": ("0_base2018", "4_decline")}
panel = pd.read_parquet(PROC / "analysis_bond_panel.parquet", columns=["date", "poa", "rent", "seg"])
panel = panel[panel.poa.isin(elig.poa)].copy(); panel["ph"] = ""
for k, (a, b) in PH.items(): panel.loc[(panel.date >= a) & (panel.date <= b), "ph"] = k
panel = panel[panel.ph != ""]
def changes(seg):
    c = panel[panel.seg == seg].groupby(["poa", "ph"]).rent.agg(["median", "size"]).reset_index()
    med, n = c.pivot(index="poa", columns="ph", values="median"), c.pivot(index="poa", columns="ph", values="size")
    out = {}
    for t, (a, b) in TR.items():
        out[t] = (100 * np.log(med[b] / med[a])).where((n[a] >= 30) & (n[b] >= 30)).dropna().rename("chg").reset_index().merge(elig[["poa", "sa3", "tier", "tier_E4", "E2_rows_l3", "uni"]], on="poa")
    return out
F01, F2, H34 = changes("f01"), changes("f2"), changes("h34")

print("[1] RQ4 RULE vs CHANCE (current phases; corridor labels permuted among postcodes)")
W = ["T1", "T2", "T3"]; bench = {(s, t): d[t][d[t].tier == "Low"].chg.median() for s, d in (("f01", F01), ("f2", F2)) for t in W}
def n_pass(lab):
    above = {}
    for s, d in (("f01", F01), ("f2", F2)):
        for t in W:
            x = d[t].assign(sa3=d[t].poa.map(lab)); g = x.groupby("sa3").chg.agg(["median", "size"])
            for sa3, r in g.iterrows():
                above.setdefault(sa3, [0, 0]); above[sa3][0] += int(r["median"] > bench[(s, t)]); above[sa3][1] = max(above[sa3][1], r["size"])
    return sum(1 for a, sz in above.values() if a >= 5 and sz >= 3)
actual = elig.set_index("poa").sa3.to_dict(); obs = n_pass(actual)
labs = np.array(list(actual.values())); pcs = list(actual)
sims = np.array([n_pass(dict(zip(pcs, rng.permutation(labs)))) for _ in range(1000)])
p = sims.mean() / 20
print(f"  observed passing corridors: {obs} | random labels: mean {sims.mean():.1f}, P(>= observed) = {(sims >= obs).mean():.0%} | chance a given corridor passes ~{p:.0%}; P(0 of 6 exposed pass | chance) ~ {(1-p)**6:.0%}")

print("\n[2] BASELINE BALANCE and T1 (f01)")
t1 = F01["T1"].merge(base[["med_f01_2018", "flat_share_2018"]], left_on="poa", right_index=True).dropna(subset=["med_f01_2018"])
rk = lambda s: s.rank(pct=True); X = np.column_stack([np.ones(len(t1)), rk(t1.med_f01_2018), rk(t1.flat_share_2018)])
res = lambda y: y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
for name, col in (("E2", "E2_rows_l3"), ("E4", "uni")):
    print(f"  {name}: Spearman with T1 raw {stats.spearmanr(t1[col], t1.chg).statistic:+.2f} -> partial (baseline rent + flat share) {np.corrcoef(res(rk(t1[col]).to_numpy()), res(rk(t1.chg).to_numpy()))[0,1]:+.2f}")
print("  baseline f01 rent, High vs Low tier ($): E2", elig.groupby('tier').poa.apply(lambda s: base.loc[s, 'med_f01_2018'].median()).round(0).to_dict(), "| E4", elig.groupby('tier_E4').poa.apply(lambda s: base.loc[s, 'med_f01_2018'].median()).round(0).to_dict())
t1["stratum"] = pd.qcut(t1.med_f01_2018, 3, labels=["cheap", "mid", "dear"])
for name, col in (("E2", "E2_rows_l3"), ("E4", "uni")):
    r = []
    for s, g in t1.groupby("stratum", observed=True):
        hi, lo = g[g[col] >= g[col].median()].chg, g[g[col] < g[col].median()].chg; r.append((s, len(g), round(hi.median() - lo.median(), 1)))
    print(f"  {name} upper-half minus lower-half T1 gap within baseline-rent strata:", r)

print("\n[3] CLUSTERS CARRYING THE HIGH TIER (f01, T1)")
x = F01["T1"]
for name, col in (("E2", "tier"), ("E4", "tier_E4")):
    h = x[x[col] == "High"]; vc = h.sa3.value_counts()
    print(f"  {name}: High tier = {len(h)} postcodes in {h.sa3.nunique()} of {x.sa3.nunique()} SA3; largest cluster {vc.index[0]} holds {vc.iloc[0]}; clusters with >=3 High postcodes: {int((vc >= 3).sum())}")

print("\n[4] FLAT-MINUS-HOUSE CONTRAST: (High-Low) for small flats minus (High-Low) for 3-4BR houses, same postcodes")
for name, col in (("E2", "tier"), ("E4", "tier_E4")):
    row = []
    for t in ("T0", "T1", "CUM"):
        m = F01[t][["poa", "sa3", col, "chg"]].merge(H34[t][["poa", "chg"]], on="poa", suffixes=("_f", "_h"))
        m["chg"] = m.chg_f - m.chg_h; m = m.rename(columns={col: "tier"})
        g = m[m.tier == "High"].chg.median() - m[m.tier == "Low"].chg.median(); lo, hi = cluster_ci(m, n_boot=2000)
        row.append(f"{t}: {g:+.1f} [{lo:+.1f}, {hi:+.1f}] (n={len(m)})")
    print(f"  {name} tiers  " + " | ".join(row))
