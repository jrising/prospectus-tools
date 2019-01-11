import csv
import numpy as np
import xarray as xr

fullpath = "/shares/gcp/climate/BCSD/hierid/popwt/daily/tas/{scenario}/CCSM4/{year}/1.6.nc4"

histyears = range(1991, 2001)
lateyears = range(2090, 2100)

#hierids = ['CHN.2.18.78', 'USA.2.77', 'USA.10.360', 'IND.21.321.1287']
#hierids = ["AUS.5.393", "AUS.5.401", "AUS.5.340", "AUS.5.383", "AUS.5.333", "AUS.5.375","AUS.5.336","AUS.5.360","AUS.5.332","AUS.5.390","AUS.5.345"]
#hierids = ['OMN.6']
#hierids = ['USA.11.421', 'USA.5.221', 'USA.33.1862', 'USA.11.456', 'MEX.31.1741']
#hierids = ["USA.14.608", "USA.33.1833", "USA.3.103", "USA.3.102", "USA.3.101"]
#hierids = ["AUS.11.1302", "AUS.5.335", "AUS.5.355", "AUS.6.527", "AUS.6.686", "AUS.11.1359", "AUS.5.318", "AUS.11.1363", "AUS.11.1276", "AUS.10.1099", "AUS.10.1190", "AUS.9.1046", "AUS.11.1310"]
#hierids = ["YEM.5.Rda27c93566fb4430", "SGP", "USA.3.104", "YEM.17", "MYS.1.2", "MEX.26.R56293582978b4f00"]
hierids = ["USA.10.360","USA.5.224", "CHL.13.53.295", "ARE.3", "AUS.11.1267", "VEN.24.311", "IND.27.404.1579"]

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

with open("tas-dists_GMFD_vs_BEST.csv", 'w') as fp:
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
