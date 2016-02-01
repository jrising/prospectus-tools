## Takes a quantiles.py configuration file and generates separate
## quantiles for each model.
## Syntax: python iterquant.py <quantile-config>.yml

import os
import yaml
from lib import results, configs, impacts

config = configs.read_default_config()

allimpacts = config['only-impacts'] if config.get('only-impacts', 'all') != 'all' else impacts.allimpacts

print "Collecting all available models."
allmodels = set()
for (batch, rcp, model, realization, pvals, targetdir) in configs.iterate_valid_targets(config, allimpacts, verbose=False):
    allmodels.add(model)

outdir = config['output-dir']

if not os.path.exists(outdir):
    os.mkdir(outdir)

for model in allmodels:
    print "Processing", model
    modeloutdir = os.path.join(outdir, model)
    if not os.path.exists(modeloutdir):
        os.mkdir(modeloutdir)

    config['output-dir'] = modeloutdir
    config['only-models'] = [model]
    config['allow-partial'] = 1
    
    configpath = os.path.join(modeloutdir, "config.yml")
    with open(configpath, 'w') as fp:
        fp.write(yaml.dump(config))

    # Run the quantiles with this configuration
    os.system("python quantiles.py " + configpath)
