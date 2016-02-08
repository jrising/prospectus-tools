import sys, resource, timeit
from netCDF4 import Dataset

# Find all netcdfs within this directory
totalsize = 0
totaltime = 0

for root, dirs, files in os.walk(path):
    for filename in files:
        # Check the filename
        match = re.match(r'.+?(pr|tas|tasmin|tasmax).+?\.nc.?', filename)
        if match:
            variable = match.group(1)
            filepath = os.path.join(root, filename)
            print "Found %s: %s" % (variable, filepath)

            memstart = resource.getrusage(resource.RUSAGE_SELF)
            timestart = timeit.timeit()
            rootgrp = Dataset(filename, 'r+', format='NETCDF4')
            alldata = rootgrp.variables[variable][:,:]
            size = alldata.size[0] * alldata.size[1]
            del alldata
            timeend = timeit.timeit()
            memend = resource.getrusage(resource.RUSAGE_SELF)

            print size, ((memend[2] - memstart[2])*resource.getpagesize())/1000000.0), timeend - timestart

            totalsize += size
            totaltime += timeend - timestart
