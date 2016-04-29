import sys
from netCDF4 import Dataset

from lib import bundles

if len(sys.argv) > 3:
    column = sys.argv[3]
else:
    column = 'rebased'

reader = Dataset(sys.argv[1], 'r', format='NETCDF4')

regions = reader.variables['regions'][:]
years = reader.variables['year'][:]

if len(sys.argv) < 3:
    print "Please provide a region:"
    print filter(lambda region: region[:3] == 'USA', regions)
    exit()

region = sys.argv[2]
if region == 'global':
    region = ''
try:
    ii = int(region)
except:
    ii = regions.tolist().index(region)
    #print "Region #", ii

data = reader.variables[column][:, ii]

print "year,value"

for jj in range(len(years)):
    print str(years[jj]) + ',' + str(data[jj])
