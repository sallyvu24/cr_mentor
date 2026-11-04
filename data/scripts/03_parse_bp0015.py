import re, sys, collections
import xml.etree.ElementTree as ET
import pandas as pd
base = sys.argv[1]; out = sys.argv[2]
d = open(base + '/pivotCacheDefinition1.xml', encoding='utf-8').read()
fields = re.findall(r'<cacheField name="([^"]+)"[^>]*>(.*?)</cacheField>', d, flags=re.S)
names = [f[0] for f in fields]
shared = []
for _, body in fields:
    items = re.findall(r'<(s|n|d|m)\b(?: v="([^"]*)")?', body)
    shared.append([v for (_, v) in items])
want = ['Financial Year of Visa Grant','Month','Client Location','Sector','Applicant Type','Education Provider Registered State','Last Visa Held - Visa Category']
widx = [names.index(w) for w in want]
tot_i = names.index('Total')
acc = collections.Counter()
n = 0
for ev, el in ET.iterparse(base + '/pivotCacheRecords1.xml', events=('end',)):
    tag = el.tag.rsplit('}', 1)[-1]
    if tag == 'r':
        kids = list(el)
        key = []
        for wi in widx:
            k = kids[wi]
            key.append(shared[wi][int(k.attrib['v'])] if k.tag.endswith('x') else k.attrib.get('v'))
        tk = kids[tot_i]
        total = float(tk.attrib['v']) if tk.tag.endswith(('n',)) else 0.0
        acc[tuple(key)] += total
        n += 1
        el.clear()
print("records parsed:", n)
df = pd.DataFrame([list(k) + [v] for k, v in acc.items()], columns=['fy','month','client_loc','sector','applicant','state','last_visa','grants'])
df.to_parquet(out, index=False)
print(df.shape); print(df.groupby('state').grants.sum().sort_values(ascending=False))
