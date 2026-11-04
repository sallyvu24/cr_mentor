"""Direct-service transit accessibility from every analysis postcode to the major HE campuses (weekday AM peak)."""
import numpy as np, pandas as pd, datetime as dt, time
G = '/Users/chipi/Downloads/full_greater_sydney_gtfs_static_0/'
P = '/Users/chipi/Desktop/DATA/career_mentor/data/processed/'
t0 = time.time()
WALK_ORIGIN_M, WALK_DEST_M = 800, 600
DAY = dt.date(2026, 11, 4)                      # a Wednesday inside the feed's validity window
WIN = (7 * 3600, 9 * 3600)

cal = pd.read_csv(G + 'calendar.txt', dtype=str); cd = pd.read_csv(G + 'calendar_dates.txt', dtype=str)
ds = DAY.strftime('%Y%m%d'); wd = DAY.strftime('%A').lower()
act = set(cal[(cal[wd] == '1') & (cal.start_date <= ds) & (cal.end_date >= ds)].service_id)
act |= set(cd[(cd.date == ds) & (cd.exception_type == '1')].service_id)
act -= set(cd[(cd.date == ds) & (cd.exception_type == '2')].service_id)
print("active services on", DAY, len(act))
trips = pd.read_csv(G + 'trips.txt', usecols=['route_id', 'service_id', 'trip_id'], dtype=str)
trips = trips[trips.service_id.isin(act)]; print("active trips", len(trips))
routes = pd.read_csv(G + 'routes.txt', usecols=['route_id', 'route_type'], dtype=str)
trips = trips.merge(routes, on='route_id', how='left')

stops = pd.read_csv(G + 'stops.txt', usecols=['stop_id', 'stop_lat', 'stop_lon'], dtype={'stop_id': str}).dropna()
ex = pd.read_csv(P + 'exposure_postcode.csv', dtype={'poa': str}); pool = ex[ex.in_pool][['poa', 'lat', 'lon']]
cam = pd.read_csv(P + 'he_campuses.csv', dtype={'poa': str})
camp = cam.groupby('poa').agg(lat=('lat', 'first'), lon=('lon', 'first'), he_rows=('he_rows', 'sum'), w=('w_rows', 'sum')).reset_index()
camp = camp[camp.he_rows >= 50]; camp = camp[camp.poa.isin(pool.poa)]
print("origin postcodes", len(pool), "| major campuses in pool", len(camp))

def hav(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2); dl = np.radians(lon2 - lon1)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * 6371008.8 * np.arcsin(np.sqrt(a))
def near(points, radius, key):
    rows = []
    sl, so = stops.stop_lat.values, stops.stop_lon.values
    for r in points.itertuples():
        d = hav(r.lat, r.lon, sl, so); m = d <= radius
        rows.append(pd.DataFrame({key: r.poa, 'stop_id': stops.stop_id.values[m], 'dist_m': d[m]}))
    return pd.concat(rows, ignore_index=True)
orig = near(pool, WALK_ORIGIN_M, 'poa'); dest = near(camp, WALK_DEST_M, 'campus')
print("origin stop links", len(orig), "| dest stop links", len(dest), "| distinct origin stops", orig.stop_id.nunique(), "| dest stops", dest.stop_id.nunique())

use = set(orig.stop_id) | set(dest.stop_id)
chunks = []
for ch in pd.read_csv(G + 'stop_times.txt', usecols=['trip_id', 'departure_time', 'arrival_time', 'stop_id', 'stop_sequence'], dtype=str, chunksize=1_000_000):
    ch = ch[ch.stop_id.isin(use) & ch.trip_id.isin(set(trips.trip_id))]; chunks.append(ch)
st = pd.concat(chunks, ignore_index=True)
def secs(s): 
    p = s.str.split(':', expand=True).astype(float); return p[0] * 3600 + p[1] * 60 + p[2]
st['dep'] = secs(st.departure_time); st['arr'] = secs(st.arrival_time); st['seq'] = st.stop_sequence.astype(int)
print("stop_times kept", len(st), "| elapsed", round(time.time() - t0), "s")

O = st.merge(orig[['poa', 'stop_id']], on='stop_id'); O = O[(O.dep >= WIN[0]) & (O.dep < WIN[1])][['trip_id', 'poa', 'stop_id', 'seq', 'dep']]
D = st.merge(dest[['campus', 'stop_id']], on='stop_id')[['trip_id', 'campus', 'seq', 'arr']].rename(columns={'seq': 'seq_d'})
J = O.merge(D, on='trip_id'); J = J[(J.seq_d > J.seq) & (J.arr > J.dep)]
J['mins'] = (J.arr - J.dep) / 60
res = J.groupby(['poa', 'campus']).agg(min_mins=('mins', 'min'), trips=('trip_id', 'nunique')).reset_index()
res = res.merge(trips[['trip_id', 'route_type']].drop_duplicates('trip_id'), how='left', left_on=res.index, right_index=True) if False else res
print("poa-campus pairs with a direct AM-peak service:", len(res), "of", len(pool) * len(camp))
res.to_parquet(P + 'gtfs_poa_campus_direct.parquet', index=False)
print("elapsed", round(time.time() - t0), "s")
