## Helper functions for reading the configuration

import sys, os
import yaml
import results

def consume_config():
    if len(sys.argv) < 2:
        print "Please specify a configuration (.yml) file."
        exit()
    
    argv = []
    config = {}
    if sys.argv[1][-4:] == '.yml':
        config = read_config(sys.argv[1])
        startii = 2
    else:
        startii = 1

    for arg in sys.argv[startii:]:
        if arg[0:2] == '--':
            if '=' in arg:
                chunks = arg[2:].split('=')
                if chunks[0] == 'config':
                    config = read_config(chunks[1])
                else:
                    config[chunks[0]] = yaml.load(chunks[1])
            else:
                config[arg[2:]] = True
        else:
            argv.append(arg)

    return config, argv

def read_config(filename):
    with open(filename, 'r') as fp:
        config = yaml.load(fp)
        return config

def iterate_valid_targets(config, impacts=None, verbose=True):
    root = config['results-root']
    verbose = verbose or config.get('verbose', False)

    do_montecarlo = config.get('do-montecarlo', False)
    do_rcp_only = config.get('only-rcp', None)
    do_iam_only = config.get('only-iam', None)
    do_targetsubdirs = config.get('targetsubdirs', None)
    checks = config.get('checks', None)

    allmodels = config['only-models'] if config.get('only-models', 'all') != 'all' else None

    if do_targetsubdirs:
        iterator = results.iterate_targetdirs(root, do_targetsubdirs)
    elif do_montecarlo == 'both':
        iterator = results.iterate_both(root)        
    elif do_montecarlo:
        iterator = results.iterate_montecarlo(root)
    else:
        iterator = results.iterate_batch(root, 'median')
        # Logic for a given directory
        #if root[-1] == '/':
        #    root = root[0:-1]
        #iterator = results.iterate_batch(*os.path.split(root))

    observations = 0
    message_on_none = "No target directories."
    for batch, rcp, model, iam, ssp, targetdir in iterator:
        message_on_none = "No valid target directories."

        if checks is not None and not results.directory_contains(targetdir, checks):
            if verbose:
                print targetdir, "missing", checks
            continue

        if do_rcp_only and rcp != do_rcp_only:
            print targetdir, "not", do_rcp_only
            continue
        if do_iam_only and iam != do_iam_only:
            print targetdir, "not", do_iam_only
            continue
        if allmodels is not None and model not in allmodels:
            print targetdir, "not in", allmodels
            continue

        if impacts is None:
            observations += 1
            yield batch, rcp, model, iam, ssp, targetdir
        else:
            # Check that at least one of the impacts is here
            for impact in impacts:
                if impact + ".nc4" in os.listdir(targetdir):
                    observations += 1
                    yield batch, rcp, model, iam, ssp, targetdir
                    break

    if observations == 0:
        print message_on_none

def interpret_filenames(argv, config):
    columns = []
    basenames = []
    transforms = []
    vectransforms = []
    for basename in argv:
        if basename[0] == '-':
            basename = basename[1:]
            transforms.append(lambda x: -x)
            vectransforms.append(lambda x: -x)
        else:
            transforms.append(lambda x: x)
            vectransforms.append(lambda x: x)
        if ':' in basename:
            columns.append(basename.split(':')[1])
            basename = basename.split(':')[0]
            if basename == '':
                assert len(basenames) > 0, "Must have a previous basename to duplicate."
                basename = basenames[-1]
        else:
            columns.append(config.get('column', None))
            
        basenames.append(basename)

    return columns, basenames, transforms, vectransforms
        
## Plural handling

def is_allregions(config):
    return not ('region' in config or 'regions' in config) and not 'region' in config.get('file-organize', [])

def get_regions(config, allregions):
    if 'region' in config:
        return [config['region']]

    regions = config.get('regions', allregions)
    if 'countries' in regions:
        regions = filter(lambda x: x != 'countries', regions) + filter(lambda x: len(x) == 3, allregions)
    if 'funds' in regions:
        regions = filter(lambda x: x != 'funds', regions) + filter(lambda x: x[:5] == 'FUND-', allregions)

    return regions

def get_years(config, years):
    if 'year' in config:
        return [config['year']]
    return config.get('years', years)

## CSV Creation

def csv_organize(rcp, ssp, region, year, config):
    values = dict(rcp=rcp, ssp=ssp, region=region, year=year)
    file_organize = config.get('file-organize', ['rcp', 'ssp'])
    allkeys = ['rcp', 'ssp', 'region', 'year']

    if 'output-file' in config:
        return (), tuple(allkeys)
    else:
        return tuple([values[key] for key in file_organize]), tuple([values[key] for key in csv_rownames(config)])

def csv_makepath(filestuff, config):
    if 'output-file' in config:
        return config['output-file']
    
    outdir = config['output-dir']

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    suffix = config.get('suffix', '')
    suffix = suffix.format(**config)

    return os.path.join(outdir, '-'.join(list(filestuff)) + suffix + '.csv')

def csv_rownames(config):
    allkeys = ['rcp', 'ssp', 'region', 'year']
    file_organize = config.get('file-organize', ['rcp', 'ssp'])
    return [key for key in allkeys if key not in file_organize]

def csv_organized_rcp(filestuff, rowstuff, config):
    file_organize = config.get('file-organize', ['rcp', 'ssp'])
    if 'rcp' in file_organize:
        return filestuff[file_organize.index('rcp')]

    return rowstuff[csv_rownames(config).index('rcp')]

do_region_sort = False

def csv_sorted(rowstuffs, config):
    file_organize = config.get('file-organize', ['rcp', 'ssp'])
    if 'year' in file_organize and 'region' in file_organize:
        return rowstuffs

    names = csv_rownames(config)
    regionorder = config['regionorder']

    if 'year' not in file_organize and 'region' not in file_organize:
        yearcol = names.index('year')
        regioncol = names.index('region')
        if do_region_sort:
            key = lambda rowstuff: (rowstuff[yearcol], rowstuff[regioncol])
            simplecmp = lambda a, b: -1 if a < b else (0 if a == b else 1)
            cmp = lambda a, b: regionorder.index(b[1]) - regionorder.index(a[1]) if a[0] == b[0] else simplecmp(a[0], b[0])
        else:
            key = lambda rowstuff: rowstuff[yearcol]
            cmp = None
    elif 'year' not in file_organize:
        yearcol = names.index('year')
        key = lambda rowstuff: rowstuff[yearcol]
        cmp = None
    else:
        regioncol = names.index('region')
        key = lambda rowstuff: rowstuff[regioncol]
        cmp = regionorder.index(b) - regionorder.index(a)

    if cmp is None:
        return sorted(rowstuffs, key=key)
    else:
        return sorted(rowstuffs, cmp=cmp, key=key)
