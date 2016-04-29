import os, sys, csv
import numpy as np

rcp = sys.argv[1]
directory = sys.argv[2]

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
    if rcp not in filename:
        continue
    print filename

    years, actuals = read_single(os.path.join(directory, filename))
    allvalues.append(actuals)

print len(allvalues)

# Construct the quantiles
filename = directory + '-' + rcp + '.csv'
with open(filename, 'w') as fp:
    writer = csv.writer(fp)
    writer.writerow(['year', 'median'])
    for ii in range(len(allvalues[0])):
        writer.writerow([years[ii], np.median([values[ii] for values in allvalues])])
