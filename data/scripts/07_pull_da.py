"""Pull residential development applications (DAs) lodged 2022-01..2026-09 from the NSW Planning Portal
Online DA API and flatten them to processed/da_residential_2022_2026.parquet.

API: https://api.apps1.nsw.gov.au/eplanning/data/v0/OnlineDA  (GET; paging and filters are sent as headers).
Resumable: one raw JSON file per month under raw/nsw_da/.  Pulling all 57 months takes roughly three hours, so by default only January and July of each year are
sampled (10 months, evenly spread). Pass `--all` as the second argument to pull every month.
Usage: python 07_pull_da.py <data_root> [--all]
"""
import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
RAW = ROOT / "raw" / "nsw_da"
RAW.mkdir(parents=True, exist_ok=True)
URL = "https://api.apps1.nsw.gov.au/eplanning/data/v0/OnlineDA"
PAGE_SIZE = 100


def headers(page, d0, d1):
    flt = {"filters": {"ApplicationType": "Development Application", "DevelopmentCategory": ["Residential"],
                       "LodgementDateFrom": d0, "LodgementDateTo": d1}}
    return {"PageSize": str(PAGE_SIZE), "PageNumber": str(page), "filters": json.dumps(flt)}


def get_page(page, d0, d1):
    for attempt in range(4):
        try:
            r = requests.get(URL, headers=headers(page, d0, d1), timeout=90)
            if r.status_code == 200:
                return r.json()
            print("HTTP", r.status_code, "retry", attempt, flush=True)
        except requests.RequestException as exc:
            print("ERR", exc, "retry", attempt, flush=True)
        time.sleep(2 + 3 * attempt)
    raise RuntimeError(f"failed {d0} {d1} page {page}")


def pull_month(period):
    fp = RAW / f"da_res_{period}.json"
    if fp.exists():
        return
    d0 = period.start_time.strftime("%Y-%m-%d")
    d1 = period.end_time.strftime("%Y-%m-%d")
    apps, page, total = [], 1, None
    while True:
        j = get_page(page, d0, d1)
        total = j["TotalPages"] if total is None else total
        apps += j["Application"]
        if page >= total:
            break
        page += 1
        time.sleep(0.25)
    fp.write_text(json.dumps(apps))
    print(period, len(apps), flush=True)


def flatten(only=None):
    rows = []
    for fp in sorted(RAW.glob("da_res_*.json")):
        if only is not None and fp.stem.replace("da_res_", "") not in only:
            continue
        for a in json.loads(fp.read_text()):
            loc = (a.get("Location") or [{}])[0]
            rows.append({
                "pan": a.get("PlanningPortalApplicationNumber"),
                "lodged": a.get("LodgementDate"), "determined": a.get("DeterminationDate"),
                "status": a.get("ApplicationStatus"), "cost": a.get("CostOfDevelopment"),
                "dwellings": a.get("NumberOfNewDwellings"), "storeys": a.get("NumberOfStoreys"),
                "council": (a.get("Council") or {}).get("CouncilName"),
                "dev_types": "|".join(t["DevelopmentType"] for t in a.get("DevelopmentType", [])),
                "postcode": loc.get("Postcode"), "suburb": loc.get("Suburb"),
                "x": pd.to_numeric(loc.get("X"), errors="coerce"), "y": pd.to_numeric(loc.get("Y"), errors="coerce"),
            })
    df = pd.DataFrame(rows)
    df["lodged"] = pd.to_datetime(df["lodged"], errors="coerce")
    df["determined"] = pd.to_datetime(df["determined"], errors="coerce")
    out = ROOT / "processed" / "da_residential_2022_2026.parquet"
    df.to_parquet(out, index=False)
    print("flattened", len(df), "->", out, flush=True)


if __name__ == "__main__":
    months = pd.period_range("2022-01", "2026-09", freq="M")
    if "--all" not in sys.argv:
        months = [m for m in months if m.month in (1, 7)]
    for p in months:
        pull_month(p)
    flatten(only=None if "--all" in sys.argv else {str(m) for m in months})
