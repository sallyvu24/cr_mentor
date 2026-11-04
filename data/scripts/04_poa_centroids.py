"""Area-weighted centroids (lon/lat) of ABS POA 2021 polygons for NSW postcodes (2xxx).
Usage: python 04_poa_centroids.py <data_root>
Needs raw/abs_poa/POA_2021_AUST_GDA2020_SHP.zip and the GCCSA correspondence (for the in_gs flag)."""
import math, sys, zipfile
from pathlib import Path
import pandas as pd, shapefile
root = Path(sys.argv[1]); raw = root / "raw"
zipfile.ZipFile(raw / "abs_poa" / "POA_2021_AUST_GDA2020_SHP.zip").extractall(raw / "abs_poa" / "shp")
sf = shapefile.Reader(str(raw / "abs_poa" / "shp" / "POA_2021_AUST_GDA2020"))
g = pd.read_excel(raw / "abs_corr" / "extracted" / "CG_POA_2021_GCCSA_2021.xlsx", dtype=str); g["r"] = g.RATIO_FROM_TO.astype(float)
gs = g[g.GCCSA_CODE_2021 == "1GSYD"].groupby("POA_CODE_2021").r.sum(); gs_pc = set(gs[gs >= 0.5].index)
rows = []
for sr in sf.iterShapeRecords():
    code = str(sr.record.as_dict()["POA_CODE21"])
    if not code.startswith("2"): continue
    shp = sr.shape; pts = shp.points; parts = list(shp.parts) + [len(pts)]
    k = math.cos(math.radians((shp.bbox[1] + shp.bbox[3]) / 2)); A = Cx = Cy = 0.0
    for i in range(len(parts) - 1):
        ring = pts[parts[i]:parts[i + 1]]; a = cx = cy = 0.0
        for j in range(len(ring) - 1):
            x0, y0, x1, y1 = ring[j][0] * k, ring[j][1], ring[j + 1][0] * k, ring[j + 1][1]
            cr = x0 * y1 - x1 * y0; a += cr; cx += (x0 + x1) * cr; cy += (y0 + y1) * cr
        A += a / 2; Cx += cx / 6; Cy += cy / 6
    if A == 0: continue
    rows.append(dict(poa=code, lon=Cx / A / k, lat=Cy / A, area_deg2=abs(A)))
df = pd.DataFrame(rows); df["in_gs"] = df.poa.isin(gs_pc)
df.to_csv(root / "processed" / "poa_centroids_nsw.csv", index=False); print(len(df), "centroids")
