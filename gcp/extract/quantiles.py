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
- do-gcmweights (default: false)
- evalqvals (default: [.17, .5, .83])
"""

import os, sys
import numpy as np
import yaml

from lib import results, bundles, weights, configs

config = configs.read_default_config()

do_gcmweights = config.get('do-gcmweights', True)
evalqvals = config.get('evalqvals', [.17, .5, .83])

basenames = []
transforms = []
for basename in sys.argv[2:]:
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
            for year, value in iterate_values(years, values, config):
                value = transforms[ii](value)
                filestuff, rowstuff in configs.csv_organize(rcp, spp, region, year, config)
                if ii == 0:
                    results.collect_in_dictionaries(data, value, filestuff, rowstuff, (batch, gcm, iam))
                else:
                    data[filestuff][rowstuff][(batch, gcm, iam)] += value

for filestuff in data:
    with open(configs.csv_makepath(filestuff, config), 'w') as fp:
        writer = csv.writer(csvfp, quoting=csv.QUOTE_MINIMAL)

        if output_format == 'edfcsv':
            writer.writerow(configs.csv_rownames(config) + map(lambda q: 'q' + str(q * 100), evalqvals))
        elif output_format == 'valuescsv':
            writer.writerow(configs.csv_rownames(config) + ['batch', 'gcm', 'iam', 'value', 'weight'])

        for rowstuff in data[filestuff]:
            model_weights = weights.get_weights(configs.csv_organized_rcp(filestuff, rowstuff, config))

            allvalues = []
            allweights = []

            for batch, gcm, iam in data[filestuff][rowstuff]:
                value = data[filestuff][rowstuff][(batch, gcm, iam)]
                if do_gcmweights:
                    weight = model_weights[gcm]
                else:
                    weight = 1
                    
                allvalues.append(value)
                allweights.append(weight)

            print filestuff, rowstuff, len(allvalues)
            if len(allvalues) == 0:
                continue

            if output_format == 'edfcsv':
                distribution = weights.WeightedECDF(allvalues, allweights)
                writer.writerow(rowstuff + list(distribution.inverse(evalqvals)))
            elif output_format == 'valuescsv':
                for ii in range(len(allvalues)):
                    writer.writerow(rowstuff + allmontevales[ii] + [allvalues[ii], allweights[ii]])

