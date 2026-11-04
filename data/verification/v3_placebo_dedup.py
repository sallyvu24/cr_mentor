"""Missing from the main notebook: (A) placebo on 3-4 bedroom houses (students rent them less than small flats),
(B) sensitivity of the small-flat result to removing the 6% exact-duplicate rows that the notebook keeps."""
import numpy as np, pandas as pd
from _common import PROC, load_pool, cluster_ci

elig = load_pool()
panel = pd.read_parquet(PROC / "analysis_bond_panel.parquet", columns=["date", "poa", "dwelling", "bedrooms", "rent", "seg", "phase"])
panel = panel[panel.poa.isin(elig.poa)]
TR = {"T0 2018->closure": ("0_base2018", "1_closure"), "T1 closure->recovery": ("1_closure", "2_recovery"),
      "T2 recovery->correction": ("2_recovery", "3_correction"), "T3 correction->plateau": ("3_correction", "4_plateau_decline"),
      "CUM 2018->plateau": ("0_base2018", "4_plateau_decline")}

def gaps(pn: pd.DataFrame, seg: str) -> pd.DataFrame:
    c = pn[pn.seg == seg].groupby(["poa", "phase"]).rent.agg(["median", "size"]).reset_index()
    med, n = c.pivot(index="poa", columns="phase", values="median"), c.pivot(index="poa", columns="phase", values="size")
    rows = []
    for name, (a, b) in TR.items():
        ch = (100 * np.log(med[b] / med[a])).where((n[a] >= 30) & (n[b] >= 30)).dropna().rename("chg").reset_index().merge(elig[["poa", "sa3", "tier"]], on="poa")
        h, l = ch[ch.tier == "High"].chg, ch[ch.tier == "Low"].chg
        lo, hi = cluster_ci(ch, n_boot=1000)
        rows.append((seg, name, len(h), len(l), round(h.median() - l.median(), 1), round(lo, 1), round(hi, 1)))
    return pd.DataFrame(rows, columns=["seg", "window", "nHigh", "nLow", "gap_pp", "lo90", "hi90"])

print("[A] Placebo: houses 3-4BR (h34)"); print(gaps(panel, "h34").to_string(index=False))
print("\n    Reference: small flats (f01)"); print(gaps(panel, "f01").to_string(index=False))
dd = panel.drop_duplicates(subset=["date", "poa", "dwelling", "bedrooms", "rent"])
print(f"\n[B] Dedup sensitivity: {len(panel):,} -> {len(dd):,} rows ({1 - len(dd) / len(panel):.1%} removed)")
print(gaps(dd, "f01").to_string(index=False))
