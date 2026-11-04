"""Build the Greater Sydney geography, HE campus table and E1/E2/E3 exposure table.

Inputs (all under data/):
  raw/abs_corr/extracted/CG_POA_2021_{GCCSA,SA4,LGA}_*.xlsx   ABS correspondences (population ratios)
  processed/poa_centroids_nsw.csv                              centroids from the ABS POA shapefile
  raw/cricos_full/cricos-{course-locations,locations,courses,institutions}.csv
  raw/doe_sa4/intl_student_sa4.xlsx                            DoE enrolments by SA4 (YTD Dec 2025)
Outputs (data/processed/):
  gs_geography.csv, he_campuses.csv, exposure_postcode.csv
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
RAW, PROC = ROOT / "raw", ROOT / "processed"

# Campus postcodes that ABS does not publish as a POA. They are institution-only postcodes;
# map each to the residential POA that contains the campus. Documented assumption.
CAMPUS_POSTCODE_OVERRIDE = {"2052": "2033",  # UNSW Kensington
                            "2109": "2113"}  # Macquarie University, North Ryde
HE_LEVEL = r"Bachelor|Master|Doctor|Graduate Cert|Graduate Dip|Associate Degree"
MAJOR_CAMPUS_MIN_ROWS = 50   # HE course-location rows for a campus to count as "major" in E3
LAMBDAS_KM = (1.5, 3.0, 5.0)
PRIMARY_LAMBDA = 3.0


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = p2 - p1
    dl = np.radians(lon2) - np.radians(lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def read_corr(name, code_col, name_col):
    d = pd.read_excel(RAW / "abs_corr" / "extracted" / name, dtype=str)
    d["r"] = d["RATIO_FROM_TO"].astype(float)
    return d.rename(columns={"POA_CODE_2021": "poa", code_col: "code", name_col: "name"})[["poa", "code", "name", "r"]]


def build_geography():
    gccsa = read_corr("CG_POA_2021_GCCSA_2021.xlsx", "GCCSA_CODE_2021", "GCCSA_NAME_2021")
    gs_ratio = gccsa[gccsa.code == "1GSYD"].groupby("poa").r.sum()
    gs = gs_ratio[gs_ratio >= 0.5].rename("gs_ratio").reset_index()

    sa4 = read_corr("CG_POA_2021_SA4_2021.xlsx", "SA4_CODE_2021", "SA4_NAME_2021")
    dom = sa4.sort_values("r", ascending=False).drop_duplicates("poa")  # dominant SA4 over ALL SA4s
    gs = gs.merge(dom.rename(columns={"name": "sa4", "r": "sa4_ratio"})[["poa", "sa4", "sa4_ratio"]], on="poa", how="left")

    sa3 = read_corr("CG_POA_2021_SA3_2021.xlsx", "SA3_CODE_2021", "SA3_NAME_2021")
    dom3 = sa3.sort_values("r", ascending=False).drop_duplicates("poa").rename(columns={"name": "sa3"})[["poa", "sa3"]]
    gs = gs.merge(dom3, on="poa", how="left")

    lga = read_corr("CG_POA_2021_LGA_2022.xlsx", "LGA_CODE_2022", "LGA_NAME_2022")
    cos = lga[lga.name == "Sydney"].groupby("poa").r.sum().rename("cos_ratio")
    gs = gs.merge(cos, on="poa", how="left")
    gs["cos_ratio"] = gs["cos_ratio"].fillna(0.0)
    gs["city_of_sydney"] = gs.cos_ratio >= 0.5
    dom_lga = lga.sort_values("r", ascending=False).drop_duplicates("poa").rename(columns={"name": "lga_dom"})[["poa", "lga_dom"]]
    gs = gs.merge(dom_lga, on="poa", how="left")

    cen = pd.read_csv(PROC / "poa_centroids_nsw.csv", dtype={"poa": str})[["poa", "lon", "lat"]]
    gs = gs.merge(cen, on="poa", how="left")
    return gs


def build_campuses(gs):
    cl = pd.read_csv(RAW / "cricos_full" / "cricos-course-locations.csv", dtype=str, encoding="utf-8-sig")
    loc = pd.read_csv(RAW / "cricos_full" / "cricos-locations.csv", dtype=str, encoding="utf-8-sig")
    loc = loc.drop_duplicates(["CRICOS Provider Code", "Location Name"])
    crs = pd.read_csv(RAW / "cricos_full" / "cricos-courses.csv", dtype=str, encoding="utf-8-sig")
    crs = crs.drop_duplicates(["CRICOS Provider Code", "CRICOS Course Code"])

    m = (cl.merge(loc[["CRICOS Provider Code", "Location Name", "Postcode"]],
                  on=["CRICOS Provider Code", "Location Name"], how="left")
           .merge(crs[["CRICOS Provider Code", "CRICOS Course Code", "Course Level", "Expired"]],
                  on=["CRICOS Provider Code", "CRICOS Course Code"], how="left"))
    n0 = len(m)
    m = m[m["Expired"] == "No"]
    print(f"[campus] course-location rows {n0}, after dropping expired courses {len(m)}")
    m = m[m["Location State"] == "NSW"]
    he = m[m["Course Level"].fillna("").str.contains(HE_LEVEL, case=False, regex=True)].copy()
    print(f"[campus] NSW HE course-location rows {len(he)}")
    he["postcode_cricos"] = he["Postcode"]
    he["poa"] = he["Postcode"].replace(CAMPUS_POSTCODE_OVERRIDE)
    he = he.merge(gs[["poa", "sa4", "lat", "lon"]], on="poa", how="left")
    in_gs = he["sa4"].notna() & he["lat"].notna()
    print(f"[campus] HE rows in Greater Sydney with centroid: {in_gs.sum()} of {len(he)}; "
          f"outside/unmapped: {(~in_gs).sum()}")
    dropped = he.loc[~in_gs, "Postcode"].value_counts().head(8)
    print("[campus] top postcodes dropped (outside Greater Sydney / no centroid):", dropped.to_dict())
    he = he[in_gs]

    campus = (he.groupby(["CRICOS Provider Code", "Institution Name", "Location Name", "postcode_cricos", "poa", "sa4", "lat", "lon"])
                .agg(he_rows=("CRICOS Course Code", "size"), he_courses=("CRICOS Course Code", "nunique"))
                .reset_index())
    return campus


def doe_he_by_sa4():
    e = pd.read_excel(RAW / "doe_sa4" / "intl_student_sa4.xlsx", header=5, usecols=range(7)).dropna(subset=["State"])
    e["Enrolments"] = pd.to_numeric(e["Enrolments"], errors="coerce")
    e["sec"] = e["Sector"].str.replace(r"\s+", " ", regex=True).str.strip().str.title()
    e = e[e["SA4 Name"].str.startswith("Sydney -")]
    out = e.pivot_table(index="SA4 Name", columns="sec", values="Enrolments", aggfunc="sum", fill_value=0)
    out.index.name = "sa4"
    return out


def main():
    gs = build_geography()
    print(f"[geo] Greater Sydney POAs: {len(gs)}; missing centroid: {gs.lat.isna().sum()}; "
          f"SA4 not 'Sydney - ': {(~gs.sa4.fillna('').str.startswith('Sydney -')).sum()}; "
          f"dominant SA4 ratio <0.8: {(gs.sa4_ratio < 0.8).sum()}; City of Sydney POAs: {gs.city_of_sydney.sum()}")
    print("[geo] POAs whose dominant SA4 is not a Sydney SA4:", gs.loc[~gs.sa4.fillna('').str.startswith('Sydney -'), ['poa', 'sa4', 'gs_ratio']].to_dict("records"))

    campus = build_campuses(gs)
    he_enrol = doe_he_by_sa4()
    he_sa4 = he_enrol["Higher Education"] if "Higher Education" in he_enrol else he_enrol.iloc[:, 0]

    # Weight variants. Primary: SA4 HE enrolments split across the SA4's campuses by HE course-location rows.
    campus["w_rows"] = 0.0
    campus["w_equal"] = 0.0
    for sa4, grp in campus.groupby("sa4"):
        tot = he_sa4.get(sa4, np.nan)
        if pd.isna(tot):
            continue
        campus.loc[grp.index, "w_rows"] = tot * grp.he_rows / grp.he_rows.sum()
        major = grp[grp.he_rows >= MAJOR_CAMPUS_MIN_ROWS]
        if len(major):
            campus.loc[major.index, "w_equal"] = tot / len(major)
        else:
            campus.loc[grp.index, "w_equal"] = tot / len(grp)
    alloc = campus.groupby("sa4")[["w_rows", "w_equal"]].sum().join(he_sa4.rename("doe_he"), how="outer")
    alloc["unallocated_rows"] = alloc.doe_he - alloc.w_rows
    print("[alloc] SA4 HE enrolments vs allocated to campuses:\n", alloc.round(0).to_string())

    # Aggregate campuses to postcode level (bond outcomes only exist at postcode level)
    cp = (campus.groupby("poa")
                .agg(lat=("lat", "first"), lon=("lon", "first"), he_rows=("he_rows", "sum"),
                     w_rows=("w_rows", "sum"), w_equal=("w_equal", "sum"), n_campuses=("Location Name", "size"))
                .reset_index())
    cp["major"] = cp.he_rows >= MAJOR_CAMPUS_MIN_ROWS

    g = gs.dropna(subset=["lat"]).copy()
    d = haversine_km(g.lat.values[:, None], g.lon.values[:, None], cp.lat.values[None, :], cp.lon.values[None, :])
    out = g[["poa", "sa4", "sa4_ratio", "sa3", "lga_dom", "city_of_sydney", "lat", "lon"]].copy()
    # ABS counts Central Coast in Greater Sydney, but it is a separate market ~80 km away. Keep it
    # in the table but flag it so the analysis pool is the 14 "Sydney - ..." SA4s.
    out["in_pool"] = out.sa4.fillna("").str.startswith("Sydney -")
    for lam in LAMBDAS_KM:
        k = np.exp(-d / lam)
        out[f"E2_rows_l{lam:g}"] = (k * cp.w_rows.values[None, :]).sum(axis=1) / 1000.0
        out[f"E2_equal_l{lam:g}"] = (k * cp.w_equal.values[None, :]).sum(axis=1) / 1000.0
    maj = cp.major.values
    out["E3_dist_major_km"] = d[:, maj].min(axis=1)
    out["E3_dist_any_km"] = d.min(axis=1)
    out["E3_nearest_major_poa"] = cp.poa.values[maj][d[:, maj].argmin(axis=1)]
    out["n_major_campuses_3km"] = (d[:, maj] <= 3.0).sum(axis=1)
    out["E3_band"] = pd.cut(out.E3_dist_major_km, [-0.01, 1.5, 3, 6, 1e9], labels=["<=1.5km", "1.5-3km", "3-6km", ">6km"])

    # E1: SA4 share of Greater Sydney enrolments (all sectors and HE), allocated through the dominant SA4
    tot_all = he_enrol.sum(axis=1)
    out["E1_share_all"] = out.sa4.map(tot_all / tot_all.sum())
    out["E1_share_he"] = out.sa4.map(he_sa4 / he_sa4.sum())

    gs.to_csv(PROC / "gs_geography.csv", index=False)
    campus.to_csv(PROC / "he_campuses.csv", index=False)
    out.to_csv(PROC / "exposure_postcode.csv", index=False)
    print(f"[out] exposure table: {len(out)} postcodes x {out.shape[1]} columns")


if __name__ == "__main__":
    main()
