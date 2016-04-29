import os, sys, csv
import numpy as np

directory = sys.argv[1]
therun = sys.argv[2]

if therun == 'aggfull':
    histclim = 'interpolated_mortality_all_ages-histclim-aggregated'
    actual = 'interpolated_mortality_all_ages-aggregated'
elif therun == 'aggdumb':
    histclim = 'interpolated_mortality_all_ages-histclim-aggregated'
    actual = 'interpolated_mortality_dumb_all_ages-aggregated'
elif therun == 'aggcoma':
    histclim = 'interpolated_mortality_all_ages-histclim-aggregated'
    actual = 'interpolated_mortality_comatose_all_ages-aggregated'
elif therun == 'aggfull0':
    histclim = None
    actual = 'interpolated_mortality_all_ages-aggregated'
elif therun == 'agghist0':
    histclim = None
    actual = 'interpolated_mortality_all_ages-histclim-aggregated'
elif therun == 'aggcost1':
    histclim = None
    actual = 'interpolated_mortality_all_ages-costs-aggregated-costs_lb'
elif therun == 'aggcost2':
    histclim = None
    actual = 'interpolated_mortality_all_ages-costs-aggregated-costs_ub'
elif therun == 'noafull':
    histclim = 'interpolated_mortality_all_ages-histclim'
    actual = 'interpolated_mortality_all_ages'
elif therun == 'noadumb':
    histclim = 'interpolated_mortality_all_ages-histclim'
    actual = 'interpolated_mortality_dumb_all_ages'
elif therun == 'noafull0':
    histclim = None
    actual = 'interpolated_mortality_all_ages'
elif therun == 'noahist0':
    histclim = None
    actual = 'interpolated_mortality_all_ages-histclim'
else:
    print "Unknown run!"
    exit()

if directory[-1] == '/':
    directory = directory[:-1] # no trailing slash!

allvalues = []

def read_single(filepath):
    years = []
    values = []
    with open(filepath, 'r') as fp:
        reader = csv.reader(fp)
        header = reader.next()
        for row in reader:
            years.append(int(row[0]))
            values.append(float(row[1]))

    return np.array(years), np.array(values)

for filename in os.listdir(directory):
    # grab the suffix
    suffixlen = 4
    while filename[-suffixlen-1] in '0123456789':
        suffixlen += 1
    suffix = filename[-suffixlen:]

    if filename[-(len(actual)+suffixlen):] != actual + suffix:
        continue

    if histclim is not None:
        histclimfile = filename[:len(filename)-(len(actual)+suffixlen)] + histclim + suffix
        print histclimfile
        if histclimfile not in os.listdir(directory):
            continue

    print filename

    try:
        years1, actuals = read_single(os.path.join(directory, filename))
        if histclim is not None:
            years2, histclims = read_single(os.path.join(directory, histclimfile))
    except:
        continue

    print "Actual", actuals[-5:]
    if histclim is not None:
        print "HistC.", histclims[-5:]

        if not np.array_equal(years1, years2):
            print "Skipping."
            continue
        allvalues.append(actuals - histclims)
    else:
        allvalues.append(actuals)

print len(allvalues)

# Construct the quantiles
if histclim is None:
    filename = directory + '-' + actual + '-nodi.csv'
else:
    filename = directory + '-' + actual + '-diff.csv'
with open(filename, 'w') as fp:
    writer = csv.writer(fp)
    writer.writerow(['year', 'median'])
    for ii in range(len(allvalues[0])):
        writer.writerow([years1[ii], np.median([values[ii] for values in allvalues])])
