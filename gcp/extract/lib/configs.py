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
        return config

def iterate_valid_targets(config, impacts=None, verbose=True):
    root = config['results-root']

    do_montecarlo = config['do-montecarlo']
    do_rcp_only = config['only-rcp']
    
    allmodels = config['only-models'] if config.get('only-models', 'all') != 'all' else None

    if do_montecarlo:
        iterator = results.iterate_montecarlo(root)
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
