import re, sys, time, requests, pathlib
R = pathlib.Path('/Users/chipi/Desktop/DATA/career_mentor/data/raw'); UA = {"User-Agent": "Mozilla/5.0 (research)"}
def get(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists(): return dest.stat().st_size
    for attempt in range(4):
        try:
            r = requests.get(url, headers=UA, timeout=(15, 120), allow_redirects=True); r.raise_for_status()
            dest.write_bytes(r.content); time.sleep(0.4); return len(r.content)
        except Exception as exc:
            print("retry", attempt, dest.name, type(exc).__name__, flush=True); time.sleep(3 + 4 * attempt)
    print("FAILED", dest.name, flush=True); return -1
base = "https://dcj.nsw.gov.au"
h = open('src/dcj.html', encoding='utf-8', errors='ignore').read()
links = sorted(set(re.findall(r'href="([^"]+\.xlsx?)"', h)))
n = 0
for l in links:
    fn = l.rsplit('/', 1)[1]
    m = re.match(r'issue-(\d+)-rent-tables', fn)
    if m and 123 <= int(m.group(1)) <= 142:               # Mar 2018 .. Dec 2022 quarters
        get(base + l if l.startswith('/') else l, R/'dcj_rent'/fn); n += 1
print("DCJ rent files:", n)
h = open('src/cos.html', encoding='utf-8', errors='ignore').read()
ls = sorted(set(re.findall(r'href="([^"]+housing-audit[^"]+\.pdf[^"]*)"', h)))
for l in ls:
    fn = re.search(r'(housing-audit[^/]*?\d{4})', l).group(1) + ".pdf"
    sz = get(l if l.startswith('http') else "https://www.cityofsydney.nsw.gov.au" + l, R/'cos_housing_audit'/fn); print(fn, sz)
sz = get("https://www.abs.gov.au/census/find-census-data/datapacks/download/2021_GCP_POA_for_NSW_short-header.zip", R/'abs_census'/'2021_GCP_POA_for_NSW_short-header.zip'); print("census", sz)
sz = get("https://datasets.seed.nsw.gov.au/dataset/4bd6f23e-1eca-41e0-b947-336ad0b05e60/resource/59867eb4-e95a-4421-9e8f-07c9af48f230/download/housingsupplydashboard_datasheet.xlsx", R/'nsw_housing_supply'/'housingsupplydashboard_datasheet.xlsx'); print("housing supply", sz)
