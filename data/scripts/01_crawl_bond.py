import sys, re, time, json, os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
PAGE = "https://www.nsw.gov.au/housing-and-construction/rental-forms-surveys-and-data/rental-bond-data"
out = sys.argv[1]
H = {"User-Agent": "Mozilla/5.0 (research; career_mentor project)"}
r = requests.get(PAGE, headers=H, timeout=60); r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")
links = []
for a in soup.find_all("a", href=True):
    h = a["href"]
    if h.lower().endswith(".xlsx") and "/noindex/" in h:
        links.append((a.get_text(" ", strip=True), urljoin(PAGE, h)))
print("xlsx links found:", len(links))
def kind(u, t):
    s = (u + " " + t).lower()
    if "refund" in s: return "refunds"
    if "held" in s: return "bondsheld"
    if "lodgement" in s or "lodgment" in s or "lodgements" in s: return "lodgements"
    return "other"
rows = [dict(text=t, url=u, kind=kind(u, t)) for t, u in links]
from collections import Counter
print(Counter(x["kind"] for x in rows))
json.dump(rows, open(os.path.join(out, "_manifest.json"), "w"), indent=1)
want = [x for x in rows if x["kind"] == "lodgements"]
ok = fail = 0
for x in want:
    fn = x["url"].rsplit("/", 1)[1]
    fp = os.path.join(out, fn)
    if os.path.exists(fp): ok += 1; continue
    try:
        rr = requests.get(x["url"], headers=H, timeout=120); rr.raise_for_status()
        open(fp, "wb").write(rr.content); ok += 1
    except Exception as e:
        fail += 1; print("FAIL", x["url"], e)
    time.sleep(0.4)
print("downloaded/ok:", ok, "failed:", fail)
