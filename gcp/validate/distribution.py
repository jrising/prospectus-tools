import csv
import numpy as np
import xarray as xr

fullpath = "/shares/gcp/climate/BCSD/hierid/popwt/daily/tas/{scenario}/CCSM4/{year}/1.6.nc4"

histyears = range(1991, 2001)
lateyears = range(2090, 2100)

hierids = ['USA.10.367', 'ETH.8.39.Rce1a51acb321322b', 'AUS.11.1392', 'AGO.11.94', 'OMN.8', 'ARE.1', 'USA.27.1625']

histdists = {hierid: [] for hierid in hierids}
for year in histyears:
    ds = xr.open_dataset(fullpath.format(scenario='historical', year=year))
    for hierid in hierids:
        histdists[hierid].extend(ds.sel(hierid=hierid).tas.values)

latedists = {hierid: [] for hierid in hierids}
for year in lateyears:
    ds = xr.open_dataset(fullpath.format(scenario='rcp85', year=year))
    for hierid in hierids:
        latedists[hierid].extend(ds.sel(hierid=hierid).tas.values)

mintemp = np.inf
maxtemp = -np.inf
for hierid in hierids:
    mintemp = min(mintemp, min(histdists[hierid]), min(latedists[hierid]))
    maxtemp = max(maxtemp, max(histdists[hierid]), max(latedists[hierid]))

mintemp = int(np.floor(mintemp))
    
with open("tas-dists.csv", 'w') as fp:
    writer = csv.writer(fp)
    aboves = range(mintemp, int(maxtemp)+2)
    writer.writerow(['hierid', 'period'] + ['abv%d' % tt for tt in aboves])
    for hierid in hierids:
        counts = list(np.bincount(np.int_(histdists[hierid]) - mintemp))
        if len(counts) < len(aboves):
            counts.extend(np.zeros(len(aboves) - len(counts)))
        writer.writerow([hierid, 'historical'] + counts)
        counts = list(np.bincount(np.int_(latedists[hierid]) - mintemp))
        if len(counts) < len(aboves):
            counts.extend(np.zeros(len(aboves) - len(counts)))
        writer.writerow([hierid, 'latercp85'] + counts)
