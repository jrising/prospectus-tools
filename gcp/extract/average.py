import sys
from netCDF4 import Dataset

from lib import bundles

startyear = int(sys.argv[2])
finalyear = int(sys.argv[3])

if len(sys.argv) > 4:
    column = sys.argv[4]
else:
    column = 'rebased'

reader = Dataset(sys.argv[1], 'r', format='NETCDF4')

regions = reader.variables['regions'][:]
years = reader.variables['year'][:]

included = (years >= startyear) * (years <= finalyear)

print "region,value"

for ii in range(len(regions)):
    print regions[ii] + ',' + str(np.mean(reader.variables[column][included, ii]))

