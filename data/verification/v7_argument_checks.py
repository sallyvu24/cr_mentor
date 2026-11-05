"""Argument-level checks of the main notebook (not a re-run of it). Each block tests ONE inferential step:
[1] 'annual and monthly files hold essentially the same rows' (3.1)  - count ratio vs row-level identity
[2] heaping of rents and what it does to medians of +-1-3 pp gaps      (4.2, 6)
[3] 'compare changes not levels' (3.5)                                 - are tiers balanced at baseline? does the gap survive stratification?
[4] cluster bootstrap with few treated clusters (6)
[5] RQ4 rule '>=5 of 6 windows above benchmark'                         - how often does pure chance pass it?
[6] seasonality signal (4.4)                                           - composition (studio vs 1BR) and postcode-level detrending
[7] 'a shared cycle dominates' (4.3/10.1)                                - size of tier differences relative to the common movement"""
import numpy as np, pandas as pd
from scipy import stats
from _common import PROC, load_pool

rng = np.random.default_rng(42)
elig = load_pool()
base = pd.read_csv(PROC / "postcode_baseline.csv", dtype={"poa": str}).set_index("poa")
raw = pd.read_parquet(PROC / "bond_lodgements_raw.parquet", columns=["date", "postcode", "dwelling", "bedrooms", "rent", "file_kind"])

print("[1] ANNUAL vs MONTHLY FILES: same count is not the same rows")
key = ["date", "postcode", "dwelling", "bedrooms", "rent"]
for yr in (2022, 2024):
    r = raw[raw.date.dt.year == yr]
    a, m = r[r.file_kind == "annual"][key].fillna(-1), r[r.file_kind == "monthly"][key].fillna(-1)
    ca, cm = a.value_counts(), m.value_counts()
    j = pd.concat([ca.rename("a"), cm.rename("m")], axis=1).fillna(0)
    print(f"  {yr}: annual {len(a):,} | monthly {len(m):,} | rows only in annual {int((j.a - j.m).clip(lower=0).sum()):,} | only in monthly {int((j.m - j.a).clip(lower=0).sum()):,}")

panel = pd.read_parquet(PROC / "analysis_bond_panel.parquet", columns=["date", "poa", "bedrooms", "rent", "seg", "phase", "sa3"])
panel = panel[panel.poa.isin(elig.poa)]
f01 = panel[panel.seg == "f01"]
print("\n[2] RENT HEAPING (f01, pool)")
r = f01.rent
print(f"  multiple of $10: {(r % 10 == 0).mean():.0%} | multiple of $50: {(r % 50 == 0).mean():.0%} | at $400/$500/$600: {((r.isin([400, 500, 600])).mean()):.0%}")
c = f01.groupby(["poa", "phase"]).rent.median()
print(f"  postcode-phase medians that are a multiple of $10: {(c % 10 == 0).mean():.0%} -> one $10 step on a $450 median = {10/450:.1%} (cf. gaps of 1-3 pp reported as findings)")

def changes(seg, a, b, min_n=30):
    cell = panel[panel.seg == seg].groupby(["poa", "phase"]).rent.agg(["median", "size"]).reset_index()
    med, n = cell.pivot(index="poa", columns="phase", values="median"), cell.pivot(index="poa", columns="phase", values="size")
    return (100 * np.log(med[b] / med[a])).where((n[a] >= min_n) & (n[b] >= min_n)).dropna().rename("chg").reset_index().merge(elig[["poa", "sa3", "tier", "E2_rows_l3"]], on="poa")

t1 = changes("f01", "1_closure", "2_recovery").merge(base[["med_f01_2018", "flat_share_2018"]], left_on="poa", right_index=True)
print("\n[3] BASELINE BALANCE and STRATIFIED GAP (f01, T1)")
print(t1.groupby("tier")[["med_f01_2018", "flat_share_2018"]].median().round(2).T.to_string())
print(f"  Spearman(baseline 2018 rent, T1 change) = {stats.spearmanr(t1.med_f01_2018, t1.chg, nan_policy='omit').statistic:+.2f} | Spearman(E2, baseline rent) = {stats.spearmanr(t1.E2_rows_l3, t1.med_f01_2018, nan_policy='omit').statistic:+.2f}")
rk = lambda s: s.rank(pct=True)
d = t1.dropna(subset=["med_f01_2018"]).copy()
X = np.column_stack([np.ones(len(d)), rk(d.med_f01_2018), rk(d.flat_share_2018)])
res = lambda y: y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
print(f"  Spearman(E2, T1) raw {stats.spearmanr(d.E2_rows_l3, d.chg).statistic:+.2f} -> partial (controls: baseline rent rank, flat-share rank) {np.corrcoef(res(rk(d.E2_rows_l3).to_numpy()), res(rk(d.chg).to_numpy()))[0,1]:+.2f}")
d["stratum"] = pd.qcut(d.med_f01_2018, 3, labels=["cheap", "mid", "dear"])
rows = []
for s, g in d.groupby("stratum", observed=True):
    hi = g[g.E2_rows_l3 >= g.E2_rows_l3.median()].chg; lo = g[g.E2_rows_l3 < g.E2_rows_l3.median()].chg
    rows.append((s, len(g), round(hi.median() - lo.median(), 1)))
print("  within baseline-rent strata, upper-half minus lower-half E2, T1 gap (pp):", rows)

print("\n[4] CLUSTER BOOTSTRAP: how many clusters carry each tier? (f01, T1)")
cl = t1.groupby("tier").sa3.nunique().to_dict(); print("  distinct SA3 per tier:", cl, "| total SA3:", t1.sa3.nunique())
print("  High-tier postcodes by SA3:", t1[t1.tier == "High"].sa3.value_counts().to_dict())

print("\n[5] RQ4 RULE: how many corridors pass '>= 5 of 6' by chance? (labels of SA3 permuted across postcodes)")
chg = {(s, t): changes(s, a, b) for s in ("f01", "f2") for t, (a, b) in {"T1": ("1_closure", "2_recovery"), "T2": ("2_recovery", "3_correction"), "T3": ("3_correction", "4_plateau_decline")}.items()}
bench = {k: v[v.tier == "Low"].chg.median() for k, v in chg.items()}
def n_pass(labels_by_poa):
    above = {}
    for k, v in chg.items():
        x = v.assign(sa3=v.poa.map(labels_by_poa)); g = x.groupby("sa3").chg.agg(["median", "size"])
        for sa3, row in g.iterrows():
            above.setdefault(sa3, [0, row["size"]]); above[sa3][0] += int(row["median"] > bench[k]); above[sa3][1] = max(above[sa3][1], row["size"])
    return sum(1 for a, sz in above.values() if a >= 5 and sz >= 3)
actual = elig.set_index("poa").sa3.to_dict()
obs = n_pass(actual)
pcs = list(actual); labs = np.array(list(actual.values())); sims = []
for _ in range(1000):
    sims.append(n_pass(dict(zip(pcs, rng.permutation(labs)))))
sims = np.array(sims)
print(f"  observed corridors passing: {obs} | under random corridor labels: mean {sims.mean():.1f}, P(>= observed) = {(sims >= obs).mean():.0%}")

print("\n[6] SEASONALITY CHECK (Feb relative to 12-month trend, High vs Low; 2021-2026)")
post = panel[(panel.date >= "2021-01-01") & (panel.seg == "f01")].merge(elig[["poa", "tier"]], on="poa")
post = post[post.tier.isin(["High", "Low"])]; post["month"] = post.date.dt.to_period("M").dt.to_timestamp()
def feb_gap(df, by):
    out = {}
    for t, g in df.groupby("tier"):
        s = g.groupby("month").rent.median() if by == "pooled" else None
        if by == "pooled":
            ls = np.log(s); dt = (ls - ls.rolling(12, center=True, min_periods=12).mean()).dropna() * 100
        else:
            pm = g.groupby(["poa", "month"]).rent.agg(["median", "size"]).reset_index(); pm = pm[pm["size"] >= 10]
            piv = pm.pivot(index="month", columns="poa", values="median"); lp = np.log(piv)
            dd = (lp - lp.rolling(12, center=True, min_periods=12).mean()) * 100; dt = dd.mean(axis=1).dropna()
        out[t] = dt[dt.index.month == 2].mean()
    return out
for label, df, by in [("pooled, f01 as in notebook", post, "pooled"), ("pooled, 1-bedroom only", post[post.bedrooms == 1], "pooled"), ("postcode-level detrend, f01", post, "postcode"), ("postcode-level detrend, 1-bedroom only", post[post.bedrooms == 1], "postcode")]:
    o = feb_gap(df, by); print(f"  {label:42s} Feb: High {o['High']:+.1f}%  Low {o['Low']:+.1f}%  gap {o['High'] - o['Low']:+.1f} pp")

print("\n[7] 'A SHARED CYCLE DOMINATES': tier differences relative to the common movement (f01, pooled-bond phase medians, as in 4.2)")
gp = f01.merge(elig[["poa", "tier"]], on="poa").groupby(["tier", "phase"]).rent.median().unstack()
for t in ("High", "Low"):
    g = gp.loc[t]; print(f"  {t}: 2018->closure {100*np.log(g['1_closure']/g['0_base2018']):+.1f}% | closure->recovery {100*np.log(g['2_recovery']/g['1_closure']):+.1f}% | 2018->plateau {100*np.log(g['4_plateau_decline']/g['0_base2018']):+.1f}%")
