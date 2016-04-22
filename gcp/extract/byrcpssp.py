import os, sys
from lib import configs

config = configs.read_default_config()

command = "python single.py %s %s > %s"

impact = sys.argv[2]
region = sys.argv[3]

modeliams = {} # {name: count}
for batch, rcp, model, ssp, iam, targetdir in configs.iterate_valid_targets(config):
    destination = os.path.join(config['output-dir'], rcp + '-' + ssp[0:4] + '-' + region)
    if not os.path.exists(desination):
        os.mkdir(destination)

    # Choose a filename
    modeliam = model + '-' + iam.replace(' ', '_') + '-' + impact
    suffix = modeliams.get(modeliam, 0) + 1
    modeliams[modeliam] = suffix

    outfile = modeliam + (str(suffix) if suffix > 1 else '') + '.csv'

    os.system(command % (os.path.join(targetdir, impact + '.nc4'), region, os.path.join(destination, outfile)))
