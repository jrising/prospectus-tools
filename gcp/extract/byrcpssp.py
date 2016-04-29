import os, sys
from lib import configs

config = configs.read_default_config()

command = "python single.py \"%s\" %s %s > %s"

impact = sys.argv[2]
region = sys.argv[3]
if len(sys.argv) > 4:
    column = sys.argv[4]
else:
    column = ''

modeliams = {} # {name: count}
for batch, rcp, model, iam, ssp, targetdir in configs.iterate_valid_targets(config):
    destination = os.path.join(config['output-dir'], rcp + '-' + ssp[0:4] + '-' + region)

    # Choose a filename, whether or not we have the impact
    modeliam = model + '-' + iam.replace(' ', '_') + '-' + impact + ('-' + column if column != '' else '')
    suffix = modeliams.get(destination + '-' + modeliam, 0) + 1
    modeliams[destination + '-' + modeliam] = suffix

    if impact + '.nc4' not in os.listdir(targetdir):
        continue
    
    outfile = modeliam + (str(suffix) if suffix > 1 else '') + '.csv'
    if not os.path.exists(destination):
        os.makedirs(destination)

    print os.path.join(targetdir, impact + '.nc4')
    os.system(command % (os.path.join(targetdir, impact + '.nc4'), region, column, os.path.join(destination, outfile)))
