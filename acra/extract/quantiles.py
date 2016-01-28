import tarfile, os, csv, sys
import numpy as np
import yaml

from lib import results, bundles, weights, impacts

if len(sys.argv) < 2:
    print "Specify the configuration file on the command-line."

with open(sys.argv[1], 'r') as fp:
    config = yaml.load(fp)

    root = config['results-root']
    outdir = config['output-dir']

    output_format = config.get('output-format', "edfcsv")
    if output_format not in ['edfcsv', 'valuescsv']:
        print "Error: output-format must be edfcsv or valuescsv."
        exit()
    
    do_montecarlo = config['do-montecarlo']
    do_adaptation = config['do-adaptation'] == True
    do_gcmweights = config.get('do-gcmweights', True)
    do_yearsets = config['do-yearsets']
    do_yearsetmeans = config['do-yearsetmeans']
    do_rcp_only = config['only-rcp']
    do_realization_only = config['only-realization']
    allimpacts = config['only-impacts'] if config.get('only-impacts', 'all') != 'all' else impacts.allimpacts
    allmodels = config['only-models'] if config.get('only-models', 'all') != 'all' else None
    suffix = {'county': '', 'state': '-state', 'region': '-region', 'national': '-national'}[config['level']]
    column = config['column']
    allow_partial = config['allow-partial']
    checks = config['checks']
    batches = range(config['batches']) if isinstance(config['batches'], int) else config['batches']

evalpvals = list(np.linspace(.01, .99, 99))

working_suffix = suffix

if do_yearsets:
    if batches == 'truehist':
        yearses = [(0, 20), (-30, 0), (-20, 0)]
    else:
        yearses = [(2020, 2039), (2040, 2059), (2080, 2099)]
else:
    years = range(2000, 2100)

if do_yearsetmeans:
    combine_years = np.mean
else:
    combine_years = lambda x: x

if do_adaptation:
    batches = map(lambda i: 'batch-adapt-' + str(i), batches)

if not os.path.exists(outdir):
    os.mkdir(outdir)

for impact in allimpacts:
    print impact

    # Collect all available results
    data = {} # { rcp-year0 => { region => { batch-realization => { model => value } } } }

    if do_montecarlo:
        iterator = results.iterate_montecarlo(root, batches=batches)
    else:
        iterator = results.iterate_byp(root)

    for (batch, rcp, model, realization, pvals, targetdir) in iterator:
        if checks is not None and not results.directory_contains(targetdir, checks):
            print targetdir, "missing", checks
            continue

        if do_rcp_only and rcp != do_rcp_only:
            continue
        if do_realization_only and realization != do_realization_only:
            continue
        if allmodels is not None and model not in allmodels:
            continue

        if impact + suffix + ".tar.gz" not in os.listdir(targetdir):
            continue

        print targetdir

        collection = batch + '-' + realization

        # Extract the values
        for region, fp in bundles.iterate_bundle(targetdir, impact, suffix, working_suffix):
            if do_yearsets:
                values = bundles.get_yearses(fp, yearses)
            else:
                values = bundles.get_years(fp, years, column=column)

            if not values:
                continue

            if do_yearsets:
                dists = [rcp + '-' + str(years[0]) for years in yearses]
            else:
                dists = [rcp + '-' + str(year) for year in years]

            for ii in range(len(dists)):
                if ii < len(values) and values[ii] is not None:
                    impacts.collect_in_dictionaries(data, combine_years(values[ii]), dists[ii], region, collection, model)

    if batches == 'truehist':
        rcps = ['truehist']
    else:
        rcps = results.rcps

    # Combine across all batch-realizations that have all models
    for rcp in rcps:
        model_weights = weights.get_weights(rcp)

        if do_yearsets:
            dists = [rcp + '-' + str(years[0]) for years in yearses]
        else:
            dists = [rcp + '-' + str(year) for year in years]

        for dist in dists:
            if dist not in data:
                continue

            with open(os.path.join(outdir, impact + '-' + dist + '.csv'), 'w') as csvfp:
                writer = csv.writer(csvfp, quoting=csv.QUOTE_MINIMAL)
                if output_format == 'edfcsv':
                    writer.writerow(['region'] + map(lambda q: 'q' + str(q), evalpvals))
                elif output_format == 'valuescsv':
                    writer.writerow(['region', 'collection', 'model', 'value', 'weight'])

                for region in data[dist].keys():

                    allvalues = []
                    allweights = []
                    allmodels = []
                    allcollections = []

                    for collection in data[dist][region]:
                        if not do_gcmweights and allow_partial == 0:
                            print "Warning: Not using GCM weights, but still using the number of GCM weighted models for limiting batches.  Set allow-partial > 0 to remove warning."
                            allow_partial = len(model_weights)
                        if len(data[dist][region][collection]) >= (allow_partial if allow_partial > 0 else len(model_weights)):
                            if do_gcmweights:
                                (values, valueweights) = weights.weighted_values(data[dist][region][collection], model_weights)
                                if len(values) == 0:
                                    print "Cannot find any values for weighted models."
                                    continue
                                if isinstance(values[0], list):
                                    for ii in range(len(values)):
                                        allvalues += values[ii]
                                        allweights += [valueweights[ii]] * len(values[ii])
                                        allmodels += ['unimplemented-case'] * len(values[ii])
                                        allcollections += [collection] * len(values[ii])
                                else:
                                    allvalues += values
                                    allweights += valueweights
                                    allmodels += data[dist][region][collection].keys()
                                    allcollections += [collection] * len(values)
                            else:
                                allvalues += data[dist][region][collection].values()
                                allweights += [1.] * len(data[dist][region][collection])
                                allmodels += data[dist][region][collection].keys()
                                allcollections += [collection] * len(data[dist][region][collection])

                    print dist, region, len(allvalues)
                    if len(allvalues) == 0:
                        continue

                    if output_format == 'edfcsv':
                        distribution = weights.WeightedECDF(allvalues, allweights)

                        writer.writerow([region] + list(distribution.inverse(evalpvals)))
                    elif output_format == 'valuescsv':
                        for ii in range(len(allvalues)):
                            writer.writerow([region, allcollections[ii], allmodels[ii], allvalues[ii], allweights[ii]])
