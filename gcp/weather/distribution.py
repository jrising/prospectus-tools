import csv
import xarray as xr

fullpath = "/shares/gcp/climate/BCSD/hierid/popwt/daily/tas/{scenario}/CCSM4/{year}/1.6.nc4"

histyears = range(1991, 2001)
lateyears = range(2090, 2100)

hierids = ['USA.10.367', 'ETH.8.39.Rce1a51acb321322b', 'AUS.11.1392']

histdists = {hierid: [] for hierid in hierids}
for year in histyears:
    ds = xr.open_dataset(fullpath.format(scenario='historical', year=year))
    for hierid in hierids:
        histdists[hierid].extend(ds.sel(hierid=hierids).tas.values)

latedists = {hierid: [] for hierid in hierids}
for year in lateyears:
    ds = xr.open_dataset(fullpath.format(scenario='rcp85', year=year))
    for hierid in hierids:
        latedists[hierid].extend(ds.sel(hierid=hierids).tas.values)

with open("tas-dists.csv", 'w') as fp:
    writer = csv.writer(fp)
    writer.writerow(['hierid', 'period'] + ['bin%d' % tt for tt in range(-10, 50)])
    for hierid in hierids:
        writer.writerow([hierid, 'historical'] + list(np.bincount(np.round(histdists[hierid]))))
        writer.writerow([hierid, 'latercp85'] + list(np.bincount(np.round(latedists[hierid]))))
