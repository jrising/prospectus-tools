import sys
import numpy as np
from netCDF4 import Dataset

if len(sys.argv) > 3:
    column = sys.argv[3]
else:
    column = 'rebased'

reader1 = Dataset(sys.argv[1], 'r', format='NETCDF4')
reader2 = Dataset(sys.argv[2], 'r', format='NETCDF4')

regions = reader1.variables['regions'][:]
years = reader1.variables['year'][:]

for ii in range(reader1.variables[column].shape[1]):
    data1 = reader1.variables[column][:, ii]
    data2 = reader2.variables[column][:, ii]
    if not np.allclose(data1, data2): #, equal_nan=True):
        print "Failed on region", ii, regions[ii]
        first = np.where(np.logical_not(np.isclose(data1, data2)))[0][0]
        print first, data1[first], data2[first]

