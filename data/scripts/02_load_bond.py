import sys, os, re, glob, warnings
import pandas as pd, openpyxl
warnings.filterwarnings("ignore")
src, out = sys.argv[1], sys.argv[2]
EXPECT = ["Lodgement Date","Postcode","Dwelling Type","Bedrooms","Weekly Rent"]
recs, meta = [], []
for fp in sorted(glob.glob(os.path.join(src, "*.xlsx"))):
    fn = os.path.basename(fp)
    wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
    title, hdr, rows = None, None, []
    for sn in wb.sheetnames:
        ws = wb[sn]
        t, h, rr = None, None, []
        for i, r in enumerate(ws.iter_rows(values_only=True)):
            r = tuple(r) + (None,)*5
            if i == 0: t = str(r[0]).replace("\n"," ") if r[0] else ""
            if h is None:
                if r[0] and str(r[0]).strip().lower().startswith("lodgement date"):
                    h = [str(c).strip() if c is not None else "" for c in r[:5]]
                continue
            if r[0] is None and r[1] is None: continue
            rr.append(r[:5])
        if h is not None:
            title, hdr, rows = t, h, rr; break
    df = pd.DataFrame(rows, columns=EXPECT)
    df["src_file"] = fn
    kind = "annual" if re.search(r"year", fn, re.I) else "monthly"
    df["file_kind"] = kind
    recs.append(df)
    meta.append(dict(file=fn, kind=kind, sheets="|".join(wb.sheetnames), header_ok=(hdr==EXPECT), header=hdr if hdr!=EXPECT else "", rows=len(df), title=title[-40:]))
meta = pd.DataFrame(meta)
pd.set_option("display.width",250); pd.set_option("display.max_rows",200); pd.set_option("display.max_colwidth",60)
print(meta[["file","kind","header_ok","rows","title"]].to_string())
print("header mismatches:", (~meta.header_ok).sum())
df = pd.concat(recs, ignore_index=True)
print("total rows", len(df))
# types
d = df["Lodgement Date"]
print("date dtypes:", d.map(type).value_counts().to_dict())
def todate(x):
    if isinstance(x, (int,float)): return pd.Timestamp("1899-12-30") + pd.Timedelta(days=int(x))
    if hasattr(x, "year"): return pd.Timestamp(x)
    try: return pd.to_datetime(x, dayfirst=True)
    except Exception: return pd.NaT
df["date"] = d.map(todate)
print("date NaT:", df["date"].isna().sum(), "range:", df["date"].min(), df["date"].max())
for c in ["Postcode","Bedrooms","Weekly Rent"]:
    print(c, "types:", df[c].map(lambda v: type(v).__name__).value_counts().to_dict())
df["postcode"] = pd.to_numeric(df["Postcode"], errors="coerce")
df["bedrooms"] = pd.to_numeric(df["Bedrooms"], errors="coerce")
df["rent"] = pd.to_numeric(df["Weekly Rent"], errors="coerce")
df["dwelling"] = df["Dwelling Type"].astype(str).str.strip()
print("dwelling:", df["dwelling"].value_counts().to_dict())
print("bedrooms U/NaN:", df["bedrooms"].isna().sum(), " rent U/NaN:", df["rent"].isna().sum(), " postcode NaN:", df["postcode"].isna().sum())
print("rent describe:\n", df["rent"].describe(percentiles=[.01,.05,.5,.95,.99]).round(1).to_dict())
print("rent<=50 :", (df.rent<=50).sum(), " rent>=3000:", (df.rent>=3000).sum())
df["ym"] = df["date"].dt.to_period("M")
# month vs file consistency: monthly files should contain their own month
m = df[df.file_kind=="monthly"].groupby("src_file")["ym"].agg(lambda s: s.value_counts().index[0])
print("monthly file dominant month sample:\n", m.head(5).to_string())
# overlap annual vs monthly: count by ym per kind for 2022-2025
cnt = df.groupby(["ym","file_kind"]).size().unstack(fill_value=0)
cnt = cnt[(cnt.index>=pd.Period("2022-01"))&(cnt.index<=pd.Period("2025-12"))]
cnt["ratio_annual_over_monthly"] = (cnt["annual"]/cnt["monthly"]).round(3)
print("annual vs monthly counts (2022-2025) ratio summary:", cnt["ratio_annual_over_monthly"].describe().round(3).to_dict())
print(cnt.head(6).to_string())
# monthly volume series
vol = df[df.file_kind=="monthly"].groupby("ym").size()
print("monthly volume:\n", vol.to_string())
df.drop(columns=["Lodgement Date","Postcode","Bedrooms","Weekly Rent"]).to_parquet(os.path.join(out,"bond_lodgements_raw.parquet"), index=False)
meta.to_csv(os.path.join(out,"bond_file_manifest.csv"), index=False)
