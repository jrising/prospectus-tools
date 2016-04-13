import sys

from lib import bundles

column = 'debased'
region = sys.argv[2]

reader = Dataset(sys.argv[1], 'r', format='NETCDF4')

regions = reader.variables['regions'][:]
years = reader.variables['years'][:]

ii = regions.index(region)
data = reader.variables[column][:, ii]

for jj in range(len(years)):
    print years[jj], data[jj]
