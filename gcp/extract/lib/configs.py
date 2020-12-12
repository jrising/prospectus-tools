## Helper functions for reading the configuration

import sys, os, re
import yaml, csv
import numpy as np
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

def handle_multiimpact_vcv(config):
    if 'multiimpact_vcv' in config and config['multiimpact_vcv'] is not None:
        multiimpact_vcv = []
        with open(config['multiimpact_vcv'], 'r') as fp:
            reader = csv.reader(fp)
            for row in reader:
                multiimpact_vcv.append(map(float, row))
        config['multiimpact_vcv'] = np.array(multiimpact_vcv)
    else:
        config['multiimpact_vcv'] = None
    
def iterate_valid_targets(root, config, impacts=None, verbose=True):
    verbose = verbose or config.get('verbose', False)

    do_montecarlo = config.get('do-montecarlo', False)
    do_rcp_only = config.get('only-rcp', None)
    do_iam_only = config.get('only-iam', None)
    do_ssp_only = config.get('only-ssp', None)
    do_targetsubdirs = config.get('targetsubdirs', None)
    do_batchdir = config.get('batchdir', 'median')
    checks = config.get('checks', None)
    dirtree = config.get('dirtree', 'normal')

    only_models, drop_models = included_models(config)

    if dirtree == 'climate-only':
        def get_iterator():
            for alldirs in results.recurse_directories(root, 2):
                yield ['pest', alldirs[0], alldirs[1], 'NA', 'NA', alldirs[2]]
        iterator = get_iterator()
    elif do_targetsubdirs:
        iterator = results.iterate_targetdirs(root, do_targetsubdirs)
    elif do_montecarlo == 'both':
        iterator = results.iterate_both(root)        
    elif do_montecarlo:
        iterator = results.iterate_montecarlo(root)
    else:
        iterator = results.iterate_batch(root, do_batchdir)
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
        if do_ssp_only and ssp != do_ssp_only:
            print targetdir, "not", do_ssp_only
            continue
        if only_models is not None and model not in only_models:
            print targetdir, "not in", only_models
            continue
        if model in drop_models:
            print targetdir, "in", drop_models
            continue

        if impacts is None:
            if is_parallel_deltamethod(config):
                dmpath = get_deltamethod_path(targetdir, config)
                if isinstance(dmpath, dict):
                    allthere = True
                    for name in dmpath:
                        if not os.path.isdir(dmpath[name]):
                            print "deltamethod", dmpath[name], "missing 1"
                            allthere = False
                            break
                    if allthere:
                        observations += 1
                        yield batch, rcp, model, iam, ssp, targetdir
                elif os.path.isdir(dmpath):
                    observations += 1
                    yield batch, rcp, model, iam, ssp, targetdir
                elif verbose:
                    print "deltamethod", get_deltamethod_path(targetdir, config), "missing 2"
            else:
                observations += 1
                yield batch, rcp, model, iam, ssp, targetdir
        else:
            # Check that at least one of the impacts is here
            for impact in impacts:
                if impact + ".nc4" in os.listdir(multipath(targetdir, impact)):
                    if is_parallel_deltamethod(config):
                        if isinstance(targetdir, dict):
                            dmpath = os.path.join(multipath(get_deltamethod_path(targetdir, config), impact), impact + ".nc4")
                            if not os.path.isfile(dmpath):
                                print "deltamethod", dmpath, "missing 3"
                                continue
                        elif not os.path.isfile(os.path.join(targetdir, impact + ".nc4")):
                            print "deltamethod", dmpath, "missing 4"
                            continue
                    observations += 1
                    yield batch, rcp, model, iam, ssp, targetdir
                    break

    if observations == 0:
        print message_on_none

def included_models(config):
    """Handle the `only-models` and `drop-models` config options, checking validity."""
    
    only_models = config['only-models'] if config.get('only-models', 'all') != 'all' else None
    if isinstance(only_models, str):
        only_models = [only_models]
    drop_models = config.get('drop-models', 'none') if config.get('drop-models', 'none') != 'none' else []
    if isinstance(drop_models, str):
        drop_models = [drop_models]

    ## Ensure that only one of these is used (for constructing weights file names)

    if only_models and drop_models:
        only_models = [model in only_models if model not in drop_models]
        drop_models = []

    return only_models, drop_models

def is_parallel_deltamethod(config):
    dmconf = config.get('deltamethod', False)
    return isinstance(dmconf, str) or isinstance(dmconf, dict)
        
def get_deltamethod_path(path, config):
    if isinstance(path, dict):
        assert isinstance(path, dict)
        assert isinstance(config['results-root'], dict)
        assert isinstance(config['deltamethod'], dict)
        
        return {name: path[name].replace(config['results-root'][name], config['deltamethod'][name]) for name in path}

    return path.replace(config['results-root'], config['deltamethod'])

def interpret_filenames(argv, config):
    columns = []
    basenames = []
    transforms = []
    vectransforms = []
    for basename in argv:
        if basename[0] == '-':
            basename = basename[1:]
            assert basename, "Error: Cannot interpret a single dash."
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
    """Grab and parse regions to extract from file

    This handles the specification of the desired regions. Both a
    `region` (a single region as a string) and `regions` (a list of
    region names) config argument are supported, as well as some key
    names within the regions list: 'global', 'countries', and 'funds'.

    Parameters
    ----------
    config : dict
    allregions : Sequence of str
        Regions available for extraction in the target NetCDF file.

    Returns
    -------
    Iterable

    """
    if 'region' in config:
        return [config['region']]
    
    regions = config.get('regions', allregions)

    if 'global' in regions:
        regions = ['' if x == 'global' else x for x in regions]
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
    if config.get('ignore-ssp', False):
        ssp = 'NA'
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

def multipath(paths, basename):
    if isinstance(paths, dict):
        for pattern in paths:
            if re.match(pattern, basename):
                return paths[pattern]

        raise ValueError("Cannot find path pattern to match " + basename)

    return paths
