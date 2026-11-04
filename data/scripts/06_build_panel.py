"""Build the bond-level analysis panel and the postcode baseline table.

Inputs:  processed/bond_lodgements_raw.parquet   (2021 annual + 2022-01..2026-09 monthly, from load_bond.py)
         raw/nsw_bond_2018/rentalbond_lodgements_year_2018.csv   (UAT mirror of data.nsw; provenance to confirm)
         processed/exposure_postcode.csv
Outputs: processed/analysis_bond_panel.parquet     one row per cleaned bond in the analysis pool
         processed/analysis_pq_seg.parquet         postcode x quarter x segment aggregates
         processed/postcode_baseline.csv           2018 baseline + group flags per postcode
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
RAW, PROC = ROOT / "raw", ROOT / "processed"

RENT_MIN, RENT_MAX, BED_MAX = 100, 5000, 8
VALID_DWELLING = list("FHTOU")

# Phase boundaries come from NSW student-visa grants (BP0015, primary applicants, rolling 12 months):
# trough 2021-11, peak 2023-07, ~118k by mid-2024, then flat/declining. Visa grants are a flow and
# lag/lead enrolments, so these are working labels, not measured stock changes.
PHASES = [("0_base2018", None, "2018-12-31"),
          ("1_closure", "2021-01-01", "2021-11-30"),
          ("2_recovery", "2021-12-01", "2023-07-31"),
          ("3_correction", "2023-08-01", "2024-06-30"),
          ("4_plateau_decline", "2024-07-01", "2026-09-30")]


def load_2018():
    d = pd.read_csv(RAW / "nsw_bond_2018" / "rentalbond_lodgements_year_2018.csv", skiprows=3, dtype=str, encoding="utf-8-sig")
    d.columns = ["d", "postcode", "dwelling", "bedrooms", "rent"]
    d["date"] = pd.to_datetime(d["d"], format="%d/%m/%Y", errors="coerce")
    for c in ["postcode", "bedrooms", "rent"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["dwelling"] = d["dwelling"].str.strip()
    d = d.dropna(subset=["date", "postcode"])
    d["src"] = "ft_2018_uat"
    return d[["date", "postcode", "dwelling", "bedrooms", "rent", "src"]]


def load_2021_on():
    d = pd.read_parquet(PROC / "bond_lodgements_raw.parquet")
    d = d[((d.file_kind == "annual") & (d.date.dt.year == 2021)) | ((d.file_kind == "monthly") & (d.date >= "2022-01-01"))]
    d = d.rename(columns={"dwelling": "dwelling"})
    d["src"] = "nsw_gov_2021_2026"
    return d[["date", "postcode", "dwelling", "bedrooms", "rent", "src"]]


def phase_of(date):
    out = pd.Series("", index=date.index, dtype="object")
    for name, lo, hi in PHASES:
        m = (date <= hi) if lo is None else ((date >= lo) & (date <= hi))
        out[m] = name
    return out


def main():
    raw = pd.concat([load_2018(), load_2021_on()], ignore_index=True)
    n0 = len(raw)
    raw["poa"] = raw.postcode.astype(int).astype(str).str.zfill(4)
    log = {"raw rows (2018 + 2021-2026)": n0}

    ok_dw = raw.dwelling.isin(VALID_DWELLING)
    ok_rent = raw.rent.between(RENT_MIN, RENT_MAX)
    ok_bed = raw.bedrooms.between(0, BED_MAX)
    log["drop: invalid dwelling code"] = int((~ok_dw).sum())
    log["drop: rent missing or outside 100-5000"] = int((ok_dw & ~ok_rent).sum())
    log["drop: bedrooms missing/outside 0-8"] = int((ok_dw & ok_rent & ~ok_bed).sum())
    b = raw[ok_dw & ok_rent & ok_bed].copy()
    log["rows after cleaning (all NSW)"] = len(b)

    ex = pd.read_csv(PROC / "exposure_postcode.csv", dtype={"poa": str, "E3_nearest_major_poa": str})
    pool = ex[ex.in_pool]
    b = b.merge(pool.drop(columns=["lat", "lon", "in_pool"]), on="poa", how="inner")
    log["rows in analysis pool (247 Sydney-SA4 postcodes)"] = len(b)

    b["log_rent"] = np.log(b.rent)
    b["ym"] = b.date.dt.to_period("M").astype(str)
    b["q"] = b.date.dt.to_period("Q").astype(str)
    b["phase"] = phase_of(b.date)
    is_f = b.dwelling == "F"
    b["seg"] = np.select([is_f & (b.bedrooms <= 1), is_f & (b.bedrooms == 2), is_f & (b.bedrooms >= 3),
                          b.dwelling.isin(["H", "T"]) & b.bedrooms.between(3, 4)],
                         ["f01", "f2", "f3p", "h34"], default="other")
    log["rows with no phase (2019-2020 gap)"] = int((b.phase == "").sum())
    b = b[b.phase != ""]
    b.to_parquet(PROC / "analysis_bond_panel.parquet", index=False)

    agg = (b.groupby(["poa", "q", "seg"])
             .agg(n=("rent", "size"), med_rent=("rent", "median"), mean_log_rent=("log_rent", "mean"))
             .reset_index())
    agg.to_parquet(PROC / "analysis_pq_seg.parquet", index=False)

    # 2018 baseline per postcode + group flags
    b18 = b[b.phase == "0_base2018"]
    base = b18.groupby("poa").agg(n_2018=("rent", "size"), flat_share_2018=("dwelling", lambda s: (s == "F").mean())).reset_index()
    for s in ["f01", "f2", "h34"]:
        x = b18[b18.seg == s].groupby("poa").agg(**{f"n_{s}_2018": ("rent", "size"), f"med_{s}_2018": ("rent", "median")}).reset_index()
        base = base.merge(x, on="poa", how="left")
    base = pool.merge(base, on="poa", how="left")
    base["flat_heavy"] = base.flat_share_2018 >= 0.35
    base["comparator_candidate"] = (~base.city_of_sydney) & base.flat_heavy & ((base.n_f01_2018.fillna(0) + base.n_f2_2018.fillna(0)) >= 200)
    base.to_csv(PROC / "postcode_baseline.csv", index=False)

    print("== CLEANING LOG")
    for k, v in log.items():
        print(f"  {k}: {v:,}")
    print("== phase x source rows\n", b.groupby(["phase", "src"]).size().unstack(fill_value=0).to_string())
    print("== rows by seg\n", b.seg.value_counts().to_string())
    print("== 2018 monthly volume (pool)\n", b18.groupby("ym").size().to_string())


if __name__ == "__main__":
    main()
