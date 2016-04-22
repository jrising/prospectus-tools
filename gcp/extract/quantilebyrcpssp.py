import os, csv
import numpy as np

directory = '/shares/gcp/outputs/timeseries/rcp85-SSP3-global' # no trailing slash!
histclim = 'interpolated_mortality_all_ages-histclim-aggregated'
actual = 'interpolated_mortality_all_ages-aggregated'

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

    histclimfile = filename[:len(filename)-(len(actual)+suffixlen)] + histclim + suffix
    if histclimfile not in os.listdir(directory):
        continue

    print filename

    years1, actuals = read_single(os.path.join(directory, filename))
    years2, histclims = read_single(os.path.join(directory, histclimfile))

    print actuals[-5:]
    print histclims[-5:]

    assert np.array_equal(years1, years2)
    allvalues.append(actuals - histclims)

print len(allvalues)

# Construct the quantiles
with open(directory + '-' + actual + '-diff.csv', 'w') as fp:
    writer = csv.writer(fp)
    writer.writerow(['year', 'median'])
    for ii in range(len(allvalues[0])):
        writer.writerow([years1[ii], np.median([values[ii] for values in allvalues])])
