## Helper functions for reading the configuration

import sys, os
import yaml
import results

def read_default_config():
    if len(sys.argv) < 2:
        print "Specify the configuration file on the command-line."
        exit()

    return read_config(sys.argv[1])

def read_config(filename):
    with open(filename, 'r') as fp:
        config = yaml.load(fp)

        allmodels = config.get('only-models', 'all')
        allow_partial = config.get('allow-partial', 1)
        if allmodels != 'all' and allow_partial > 0 and allow_partial < len(allmodels):
            print "Warning: allow-partial specifies a value greater than the number of included models.  Setting equal to the number of models."
            config['allow-partial'] = len(allmodels)
        if allmodels != 'all' and allow_partial == 0: # interpret 0 (all) as all allowed
            config['allow-partial'] = len(allmodels)

        return config

def iterate_valid_targets(config, impacts, verbose=True):
    root = config['results-root']
    do_montecarlo = config['do-montecarlo']
    batches = range(config['batches']) if isinstance(config['batches'], int) else config['batches']
    allmodels = config['only-models'] if config.get('only-models', 'all') != 'all' else None
    checks = config['checks']
    do_rcp_only = config['only-rcp']

    if do_montecarlo:
        iterator = results.iterate_montecarlo(root, batches=batches)
    else:
        if root[-1] == '/':
            root = root[0:-1]
        iterator = results.iterate_batch(*os.path.split(root))

    for (batch, rcp, model, pvals, targetdir) in iterator:
        if checks is not None and not results.directory_contains(targetdir, checks):
            if verbose:
                print targetdir, "missing", checks
            continue

        if do_rcp_only and rcp != do_rcp_only:
            print targetdir, "not", do_rcp_only
            continue
        if allmodels is not None and model not in allmodels:
            print targetdir, "not in", allmodels
            continue

        # Check that at least one of the impacts is here
        for impact in impacts:
            if impact + suffix + ".tar.gz" in os.listdir(targetdir):
                yield (batch, rcp, model, pvals, targetdir)
                continue
