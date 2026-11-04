"""Audit of the solution against the course EDA pipeline (Day 2-4). Quantifies six places where a lecture step is thin or missing:
(a) missing-value pattern, (b) silent row loss when loading the 2018 file, (c) what the hard limits removed,
(d) cross-field consistency, (e) group-wise IQR (Day 3 boxplot-by-category idea) and its effect on the result,
(f) whether the scaling step changes anything."""
import numpy as np, pandas as pd
from scipy import stats
from _common import DATA, PROC, load_pool, cluster_ci

raw = pd.read_parquet(PROC / "bond_lodgements_raw.parquet", columns=["date", "postcode", "dwelling", "bedrooms", "rent", "file_kind"])
is21 = (raw.file_kind == "annual") & (raw.date.dt.year == 2021)
is22 = (raw.file_kind == "monthly") & (raw.date >= "2022-01-01")
src = raw[is21 | is22].copy()
src["year"] = src.date.dt.year
print(f"Analysis set before cleaning: {len(src):,}")

print("\n[a] MISSING-VALUE PATTERN (Day 2: isnull().any/all(axis=1); Day 3: look for the pattern before deciding)")
src["rent_na"], src["bed_na"] = src.rent.isna(), src.bedrooms.isna()
print("both missing:", int((src.rent_na & src.bed_na).sum()), "| rent only:", int((src.rent_na & ~src.bed_na).sum()), "| bedrooms only:", int((~src.rent_na & src.bed_na).sum()))
print("share missing by dwelling code (%):"); print((src[src.dwelling.isin(list("FHTOU"))].groupby("dwelling")[["rent_na", "bed_na"]].mean() * 100).round(2))
print("share missing by year (%):"); print((src.groupby("year")[["rent_na", "bed_na"]].mean() * 100).round(2))
print("rent missing when dwelling == 'U':", round(src[src.dwelling == "U"].rent_na.mean() * 100, 1), "% | bedrooms missing when 'U':", round(src[src.dwelling == "U"].bed_na.mean() * 100, 1), "%")

print("\n[b] SILENT ROW LOSS when loading the 2018 file (notebook 3.1: coerce + dropna, no count printed)")
b18 = pd.read_csv(DATA / "raw/nsw_bond_2018/rentalbond_lodgements_year_2018.csv", skiprows=3, dtype=str, encoding="utf-8-sig")
b18.columns = ["d", "postcode", "dwelling", "bedrooms", "rent"]
dt = pd.to_datetime(b18.d, format="%d/%m/%Y", errors="coerce"); pc = pd.to_numeric(b18.postcode, errors="coerce")
print(f"rows read {len(b18):,} | unparseable date {int(dt.isna().sum())} | unparseable postcode {int(pc.isna().sum())} | dropped by dropna {int((dt.isna() | pc.isna()).sum())}")
print("dwelling codes 2018:", b18.dwelling.str.strip().value_counts().head(8).to_dict())

print("\n[c] WHAT THE HARD LIMITS REMOVED (rows with a valid dwelling code)")
v = src[src.dwelling.isin(list("FHTOU")) & src.rent.notna()]
lo, hi = v[v.rent < 100], v[v.rent > 5000]
print(f"rent < $100: {len(lo):,} (median {lo.rent.median():.0f}) | rent > $5,000: {len(hi):,} (median {hi.rent.median():,.0f})")
print("dwelling mix of removed rows (%):", (pd.concat([lo, hi]).dwelling.value_counts(normalize=True) * 100).round(1).to_dict())
print("rent == 0:", int((v.rent == 0).sum()), "| rent between 1 and 99:", int(((v.rent > 0) & (v.rent < 100)).sum()))

print("\n[d] CROSS-FIELD CONSISTENCY on the cleaned panel (inconsistent data, Day 3 list item 3)")
pan = pd.read_parquet(PROC / "analysis_bond_panel.parquet", columns=["date", "poa", "dwelling", "bedrooms", "rent", "seg", "phase", "sa3"])
print("houses (H) recorded with 0 bedrooms:", int(((pan.dwelling == "H") & (pan.bedrooms == 0)).sum()), f"({((pan.dwelling == 'H') & (pan.bedrooms == 0)).mean() * 100:.2f}% of panel)")
print("flats (F) with >= 5 bedrooms:", int(((pan.dwelling == "F") & (pan.bedrooms >= 5)).sum()))
g = pan.groupby(["poa", "seg", pan.date.dt.year]).rent.transform("median")
ratio = pan.rent / g
print(f"rent > 3x or < 1/3 of its own postcode-segment-year median: {((ratio > 3) | (ratio < 1/3)).sum():,} rows ({((ratio > 3) | (ratio < 1/3)).mean() * 100:.2f}%)")

print("\n[e] GROUP-WISE IQR (rule applied within segment x year instead of globally) and its effect on the main result")
elig = load_pool()
f = pan[pan.seg.isin(["f01"]) & pan.poa.isin(elig.poa)].copy(); f["yr"] = f.date.dt.year
q1, q3 = f.groupby("yr").rent.transform(lambda s: s.quantile(.25)), f.groupby("yr").rent.transform(lambda s: s.quantile(.75))
flag = (f.rent < q1 - 1.5 * (q3 - q1)) | (f.rent > q3 + 1.5 * (q3 - q1))
print(f"f01 rows flagged by within-year IQR: {flag.sum():,} ({flag.mean() * 100:.1f}%)")
def t1_gap(df):
    c = df.groupby(["poa", "phase"]).rent.agg(["median", "size"]).reset_index()
    med, n = c.pivot(index="poa", columns="phase", values="median"), c.pivot(index="poa", columns="phase", values="size")
    ch = (100 * np.log(med["2_recovery"] / med["1_closure"])).where((n["1_closure"] >= 30) & (n["2_recovery"] >= 30)).dropna().rename("chg").reset_index().merge(elig[["poa", "sa3", "tier"]], on="poa")
    return ch[ch.tier == "High"].chg.median() - ch[ch.tier == "Low"].chg.median()
print(f"T1 High-minus-Low gap: all rows {t1_gap(f):+.2f} pp | after dropping flagged rows {t1_gap(f[~flag]):+.2f} pp")

print("\n[f] DOES THE SCALING STEP CHANGE ANYTHING? (notebook 3.3 min-max scales 6 exposure variants, then draws a SPEARMAN heatmap)")
ex = pd.read_csv(PROC / "exposure_postcode.csv", dtype={"poa": str}); ex = ex[ex.in_pool]
cols = ["E2_rows_l1.5", "E2_rows_l3", "E2_rows_l5", "E2_equal_l3", "E3_dist_major_km", "E1_share_he"]
mm = (ex[cols] - ex[cols].min()) / (ex[cols].max() - ex[cols].min())
print("max |difference| between Spearman matrix on RAW values and on MIN-MAX values:", float((ex[cols].corr(method="spearman") - mm.corr(method="spearman")).abs().max().max()))
print("Pearson matrix on raw vs min-max (a scale-invariant case too):", float((ex[cols].corr() - mm.corr()).abs().max().max()))
