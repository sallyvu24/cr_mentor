import pandas as pd, numpy as np
from scipy import stats
P='/Users/chipi/Desktop/DATA/career_mentor/data/processed/'
panel = pd.read_parquet(P+'analysis_bond_panel.parquet', columns=['date','poa','seg','rent','sa3'])
cen = pd.read_csv(P+'census2021_poa_features.csv', dtype={'poa':str})[['poa','uni_per_100','renter_share']]
base = pd.read_csv(P+'postcode_baseline.csv', dtype={'poa':str}); elig = base[base.city_of_sydney | base.comparator_candidate].merge(cen, on='poa', how='left')
elig['tier_E2'] = pd.qcut(elig.E2_rows_l3, 3, labels=['Low','Mid','High'])
elig['tier_E4'] = pd.qcut(elig.uni_per_100, 3, labels=['Low','Mid','High'])
print("E2 vs E4 tier agreement (share same tier):", round((elig.tier_E2==elig.tier_E4).mean(),2), "| Spearman:", round(stats.spearmanr(elig.E2_rows_l3, elig.uni_per_100).statistic,2))
panel = panel[panel.seg.isin(['f01','f2']) & panel.poa.isin(elig.poa)]
def phases(d, scheme):
    P_ = {'flow':[('b','2018-01-01','2018-12-31'),('c','2021-01-01','2021-11-30'),('r','2021-12-01','2023-07-31'),('k','2023-08-01','2024-06-30'),('d','2024-07-01','2026-09-30')],
          'stock':[('b','2018-01-01','2018-12-31'),('c','2021-01-01','2021-12-31'),('r','2022-01-01','2023-12-31'),('k','2024-01-01','2025-06-30'),('d','2025-07-01','2026-09-30')]}[scheme]
    out = pd.Series('', index=d.index)
    for n,a,b in P_: out[(d.date>=a)&(d.date<=b)] = n
    return out
def run(scheme, tiercol, nboot=1000, seed=42):
    d = panel.copy(); d['ph'] = phases(d, scheme); d = d[d.ph!='']
    cell = d.groupby(['poa','seg','ph']).rent.agg(['median','size']).reset_index()
    med = cell.pivot(index=['poa','seg'], columns='ph', values='median'); n = cell.pivot(index=['poa','seg'], columns='ph', values='size')
    T = {'T0 base→closure':('b','c'),'T1 closure→recovery':('c','r'),'T2 recovery→correction/plateau':('r','k'),'T3 →decline/plateau':('k','d'),'CUM':('b','d')}
    rows=[]
    for seg in ['f01','f2']:
        for name,(a,b) in T.items():
            ok = (n[a]>=30)&(n[b]>=30); ch = (100*np.log(med[b]/med[a])).where(ok).dropna()
            x = ch.xs(seg, level='seg').rename('chg').reset_index().merge(elig[['poa','sa3',tiercol]], on='poa')
            x = x.dropna(subset=[tiercol]); hi = x[x[tiercol]=='High'].chg; lo = x[x[tiercol]=='Low'].chg
            gap = hi.median()-lo.median()
            rng = np.random.default_rng(seed); groups = [g for _,g in x.groupby('sa3')]; reps=[]
            for _ in range(nboot):
                s = pd.concat([groups[i] for i in rng.integers(0,len(groups),len(groups))]); h=s[s[tiercol]=='High'].chg; l=s[s[tiercol]=='Low'].chg
                if len(h)>=3 and len(l)>=3: reps.append(h.median()-l.median())
            rows.append((seg,name,len(hi),len(lo),round(gap,1),round(np.percentile(reps,5),1),round(np.percentile(reps,95),1)))
    return pd.DataFrame(rows, columns=['seg','window','nH','nL','gap_pp','lo90','hi90'])
for scheme, tc in [('flow','tier_E2'),('stock','tier_E2'),('flow','tier_E4'),('stock','tier_E4')]:
    print(f"\n=== phases={scheme}, exposure tiers by {'E2 (campus-based)' if tc=='tier_E2' else 'E4 (Census uni students per 100 residents)'}")
    print(run(scheme, tc).to_string(index=False))
