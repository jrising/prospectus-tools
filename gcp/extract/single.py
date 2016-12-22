"""
Usage: `python single.py OPTIONS FILEPATH

Supported configuration options:
- config (default: none): read the options from a config file
- column (default: `rebased`)
- yearsets (default: `no`)
- year or years (default: `null`)
- region or regions (default: `null`)
"""

import sys
from netCDF4 import Dataset

from lib import bundles, configs

config, argv = configs.consume_config()

years, regions, data = bundle.read(argv[0], config.get('column', 'rebased'))

writer = csv.writer(sys.stdout)
writer.writerow(['region', 'year', 'value'])

for region in configs.get_regions(config, regions):
    if region == 'global':
        region = ''
    try:
        ii = int(region)
    except:
        ii = regions.tolist().index(region)

    for year, value in iterate_values(years, data[:, ii], config):
        writer.writerow([region, year, value])
