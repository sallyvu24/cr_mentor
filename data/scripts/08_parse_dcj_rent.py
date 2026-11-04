import glob, re, warnings, pandas as pd, numpy as np
warnings.filterwarnings("ignore")
rows = []
for f in sorted(glob.glob('/Users/chipi/Desktop/DATA/career_mentor/data/raw/dcj_rent/*.xlsx')):
    m = re.search(r'issue-(\d+)-rent-tables-(\w+)-(\d{4})', f)
    mon, yr = m.group(2), int(m.group(3)); q = {'march':1,'june':2,'september':3,'december':4}[mon]
    d = pd.read_excel(f, sheet_name='Postcode', header=5, dtype=str)
    d.columns = ['postcode','dwelling','bedrooms','q1','med','q3','n_new','n_held'] + list(d.columns[8:])
    d = d[['postcode','dwelling','bedrooms','q1','med','q3','n_new','n_held']].copy()
    d['quarter'] = pd.Period(f"{yr}Q{q}"); d['issue'] = int(m.group(1)); rows.append(d)
df = pd.concat(rows, ignore_index=True)
for c in ['q1','med','q3','n_new','n_held']:
    df[c+'_raw'] = df[c]; df[c] = pd.to_numeric(df[c], errors='coerce')
df['postcode'] = pd.to_numeric(df.postcode, errors='coerce')
df = df.dropna(subset=['postcode']); df['postcode'] = df.postcode.astype(int).astype(str).str.zfill(4)
print(df.shape, df.quarter.min(), df.quarter.max(), "quarters:", df.quarter.nunique())
print("dwelling:", df.dwelling.value_counts().to_dict()); print("bedrooms:", df.bedrooms.value_counts().to_dict())
print("suppression markers in med:", df.med_raw[df.med.isna()].value_counts().head(5).to_dict())
df.drop(columns=[c for c in df.columns if c.endswith('_raw')]).to_parquet('/Users/chipi/Desktop/DATA/career_mentor/data/processed/dcj_rent_postcode_2018_2022.parquet', index=False)
