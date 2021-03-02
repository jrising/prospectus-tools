"""
Usage: `python quantiles.py CONFIG <->BASENAME<:column>...

Supported configuration options:
- column (default: `rebased`)
- yearsets (default: `no`)
- years (default: `null`)
- regions (default: `null`)
- results-root
- output-dir
- do-montecarlo
- only-rcp
- only-iam
- only-ssp
- only-models (default: `all`)
- drop-models (default: `none`)
- deltamethod (default: `no`) -- otherwise, results root for deltamethod
- file-organize (default: rcp, ssp)
- do-gcmweights (default: true)
- evalqvals (default: ['mean', .17, .5, .83])
- ignore-missing (default: no)
"""

import os, sys, csv, traceback, yaml, copy
import numpy as np

from lib import results, bundles, weights, weights_vcv, configs

config, argv = configs.consume_config()
configs.handle_multiimpact_vcv(config)

do_gcmweights = config.get('do-gcmweights', True)
evalqvals = config.get('evalqvals', ['mean', .17, .5, .83])
output_format = config.get('output-format', 'edfcsv')

columns, basenames, transforms, vectransforms = configs.interpret_filenames(argv, config)

# Collect all available results
data, years = results.sum_into_data(config['results-root'], basenames, columns, config, transforms, vectransforms)
if configs.is_parallel_deltamethod(config):
    # corresponds to each value in data, if doing parallel deltamethod
    config2 = copy.copy(config)
    config2['deltamethod'] = True
    parallel_deltamethod_data, parallel_deltamethod_years = results.sum_into_data(config['deltamethod'], basenames, columns, config2, transforms, vectransforms)

for filestuff in data:
    print "Creating file: " + str(filestuff)
    
    if configs.is_parallel_deltamethod(config) and filestuff not in parallel_deltamethod_data:
        print str(filestuff) + " is not in delta method output. Skipping model specification..."
        continue
    
    with open(configs.csv_makepath(filestuff, config), 'w') as fp:
        writer = csv.writer(fp, quoting=csv.QUOTE_MINIMAL)
        rownames = configs.csv_rownames(config)

        if output_format == 'edfcsv':
            writer.writerow(rownames + map(lambda q: q if isinstance(q, str) else 'q' + str(int(q * 100)), evalqvals))
            if configs.is_parallel_deltamethod(config):
                encoded_evalqvals = weights_vcv.WeightedGMCDF.encode_evalqvals(evalqvals)
            else:
                encoded_evalqvals = weights.WeightedECDF.encode_evalqvals(evalqvals)
        elif output_format == 'valuescsv':
            writer.writerow(rownames + ['batch', 'gcm', 'iam', 'value', 'weight'])

            
        for rowstuff in configs.csv_sorted(data[filestuff].keys(), config):
            print "Outputing row: " + str(rowstuff)
            if do_gcmweights:
                model_weights = weights.get_weights(configs.csv_organized_rcp(filestuff, rowstuff, config), config)

            allvalues = []
            allvariances = [] # only used for parallel deltamethod
            allweights = []
            allmontevales = []

            for batch, gcm, iam in data[filestuff][rowstuff]:
                value = data[filestuff][rowstuff][(batch, gcm, iam)]
                if config.get('deltamethod', False) == True:
                    value = results.deltamethod_variance(value, config)
                    
                if do_gcmweights:
                    try:
                        weight = model_weights[gcm.lower()]
                    except:
                        print "Warning: No weight available for %s, so dropping." % gcm
                        weight = 0.
                else:
                    weight = 1.

                allvalues.append(value)
                allweights.append(weight)
                allmontevales.append([batch, gcm, iam])

                if configs.is_parallel_deltamethod(config):
                    allvariances.append(results.deltamethod_variance(parallel_deltamethod_data[filestuff][rowstuff][(batch, gcm, iam)], config))
                
            #print filestuff, rowstuff, allvalues
            if len(allvalues) == 0:
                continue

            if output_format == 'edfcsv':
                if configs.is_allregions(config):
                    assert 'all' in rowstuff
                    allvalues = np.array(allvalues)
                    if configs.is_parallel_deltamethod(config):
                        allvariances = np.array(allvariances)
                    for ii in range(allvalues.shape[1]):
                        if configs.is_parallel_deltamethod(config):
                            if np.any(np.isnan(allvalues[:, ii])):
                                print "%s has missing values. Skipping." % config['regionorder'][ii]
                                continue
                            distribution = weights_vcv.WeightedGMCDF(allvalues[:, ii], allvariances[:, ii], allweights)
                        else:
                            distribution = weights.WeightedECDF(allvalues[:, ii], allweights, ignore_missing=config.get('ignore-missing', False))
                        myrowstuff = list(rowstuff)
                        myrowstuff[rownames.index('region')] = config['regionorder'][ii]
                        writer.writerow(myrowstuff + list(distribution.inverse(encoded_evalqvals)))
                else:
                    if configs.is_parallel_deltamethod(config):
                        distribution = weights_vcv.WeightedGMCDF(allvalues, allvariances, allweights)
                    else:
                        distribution = weights.WeightedECDF(allvalues, allweights, ignore_missing=config.get('ignore-missing', False))
                        
                    writer.writerow(list(rowstuff) + list(distribution.inverse(encoded_evalqvals)))
            elif output_format == 'valuescsv':
                for ii in range(len(allvalues)):
                    if isinstance(allvalues[ii], list) or isinstance(allvalues[ii], np.ndarray):
                        if 'region' in config.get('file-organize', []) and 'year' not in config.get('file-organize', []):
                            for jj in range(min(len(allvalues[ii]), len(years))):
                                row = list(rowstuff) + allmontevales[ii] + [allvalues[ii][jj], allweights[ii]]
                                row[rownames.index('year')] = years[jj]  # still set from before
                                writer.writerow(row)
                            continue
                        
                        for jj in range(len(allvalues[ii])):
                            myrowstuff = list(rowstuff)
                            myrowstuff[rownames.index('region')] = config['regionorder'][jj]
                            writer.writerow(myrowstuff + allmontevales[ii] + [allvalues[ii][jj], allweights[ii]])
                    else:
                        writer.writerow(list(rowstuff) + allmontevales[ii] + [allvalues[ii], allweights[ii]])

