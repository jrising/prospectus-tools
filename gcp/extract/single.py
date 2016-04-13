import sys

from lib import bundles

column = 'debased'

reader = Dataset(sys.argv[1], 'r', format='NETCDF4')

regions = reader.variables['regions'][:]
years = reader.variables['years'][:]

if len(sys.argv) < 3:
    print "Please provide a region:"
    print regions
    exit()

region = sys.argv[2]
ii = regions.index(region)
data = reader.variables[column][:, ii]

for jj in range(len(years)):
    print years[jj], data[jj]
