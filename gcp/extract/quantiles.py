"""
Usage: `python quantiles.py CONFIG <->BASENAME...

Supported configuration options:
- column (default: `rebased`)
- yearsets (default: `no`)
- years (default: `null`)
- regions (default: `null`)
- result-root
- output-dir
- do-montecarlo
- only-rcp
- only-models (default: `all`)
- file-organize (default: rcp, ssp)
- do-gcmweights (default: true)
- evalqvals (default: [.17, .5, .83])
"""

import os, sys, csv
import numpy as np
import yaml

from lib import results, bundles, weights, configs

config, argv = configs.consume_config()

do_gcmweights = False #config.get('do-gcmweights', True) # Current unavailable
evalqvals = config.get('evalqvals', [.17, .5, .83])
output_format = config.get('output-format', 'edfcsv')

basenames = []
transforms = []
for basename in argv:
    if basename[0] == '-':
        basenames.append(basename[1:])
        transforms.append(lambda x: -x)
    else:
        basenames.append(basename)
        transforms.append(lambda x: x)

# Collect all available results
data = {} # { filestuff => { rowstuff => { batch-gcm-iam => value } } }

for batch, rcp, gcm, iam, ssp, targetdir in configs.iterate_valid_targets(config, basenames):
    print targetdir

    # Ensure that all basenames are accounted for
    foundall = True
    for basename in basenames:
        if basename + '.nc4' not in os.listdir(targetdir):
            foundall = False
            break
    if not foundall:
        continue
    
    # Extract the values
    for ii in range(len(basenames)):
        for region, years, values in bundles.iterate_regions(os.path.join(targetdir, basenames[ii] + '.nc4'), config):
            for year, value in bundles.iterate_values(years, values, config):
                value = transforms[ii](value)
                filestuff, rowstuff = configs.csv_organize(rcp, ssp, region, year, config)
                if ii == 0:
                    results.collect_in_dictionaries(data, value, filestuff, rowstuff, (batch, gcm, iam))
                else:
                    data[filestuff][rowstuff][(batch, gcm, iam)] += value

for filestuff in data:
    with open(configs.csv_makepath(filestuff, config), 'w') as fp:
        writer = csv.writer(fp, quoting=csv.QUOTE_MINIMAL)

        if output_format == 'edfcsv':
            writer.writerow(configs.csv_rownames(config) + map(lambda q: 'q' + str(q * 100), evalqvals))
        elif output_format == 'valuescsv':
            writer.writerow(configs.csv_rownames(config) + ['batch', 'gcm', 'iam', 'value', 'weight'])

        for rowstuff in configs.csv_sorted(data[filestuff].keys(), config):
            if do_gcmweights:
                model_weights = weights.get_weights(configs.csv_organized_rcp(filestuff, rowstuff, config))

            allvalues = []
            allweights = []
            allbatch = []
            allgcm = []
            alliam = []

            for batch, gcm, iam in data[filestuff][rowstuff]:
                value = data[filestuff][rowstuff][(batch, gcm, iam)]
                if do_gcmweights:
                    weight = model_weights[gcm]
                else:
                    weight = 1.
                    
                allvalues.append(value)
                allweights.append(weight)
                allbatch.append(batch)
                allgcm.append(gcm)
                alliam.append(iam)

            #print filestuff, rowstuff, allvalues
            if len(allvalues) == 0:
                continue

            if output_format == 'edfcsv':
                distribution = weights.WeightedECDF(allvalues, allweights)
                writer.writerow(list(rowstuff) + list(distribution.inverse(evalqvals)))
            elif output_format == 'valuescsv':
                for ii in range(len(allvalues)):
                    writer.writerow(list(rowstuff) + [allbatch[ii], allgcm[ii], alliam[ii], allvalues[ii], allweights[ii]])

