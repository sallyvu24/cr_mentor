"""Shared helpers for the verification scripts. Paths are resolved from this file, so nothing is hard-coded."""
from pathlib import Path
import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parents[1]
PROC = DATA / "processed"
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 40)


def load_pool() -> pd.DataFrame:
    """The 117 comparison postcodes (13 City of Sydney + 104 flat-heavy comparators) with E2 tertiles."""
    base = pd.read_csv(PROC / "postcode_baseline.csv", dtype={"poa": str})
    elig = base[base.city_of_sydney | base.comparator_candidate].copy()
    elig["tier"] = pd.qcut(elig.E2_rows_l3, 3, labels=["Low", "Mid", "High"]).astype(str)
    return elig


def cluster_ci(x: pd.DataFrame, col: str = "chg", tier_col: str = "tier", n_boot: int = 2000, seed: int = 42):
    """90% interval for the High-minus-Low gap in medians, resampling whole SA3 corridors (same method as the main notebook)."""
    rng = np.random.default_rng(seed)
    groups = [g for _, g in x.groupby("sa3")]
    reps = []
    for _ in range(n_boot):
        s = pd.concat([groups[i] for i in rng.integers(0, len(groups), len(groups))])
        h, l = s.loc[s[tier_col] == "High", col], s.loc[s[tier_col] == "Low", col]
        if len(h) >= 3 and len(l) >= 3:
            reps.append(h.median() - l.median())
    return (np.percentile(reps, 5), np.percentile(reps, 95)) if reps else (np.nan, np.nan)
