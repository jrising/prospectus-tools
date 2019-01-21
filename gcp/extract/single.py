"""
Usage: `python single.py OPTIONS FILEPATH

Supported configuration options:
- config (default: none): read the options from a config file
- column (default: `rebased`)
- yearsets (default: `no`)
- year or years (default: `null`)
- region or regions (default: `null`)
"""

import sys, csv
from lib import bundles, configs

config, argv = configs.consume_config()
columns, basenames, transforms, vectransforms = configs.interpret_filenames(argv, config)

data = {} # {region => { year => value }}

for ii in range(len(basenames)):
    for region, years, values in bundles.iterate_regions(basenames[ii], columns[ii], config):
        if region not in data:
            data[region] = {}
        for year, value in bundles.iterate_values(years, values, config):
            if region == 'all':
                value = vectransforms[ii](value)
            else:
                value = transforms[ii](value)

            if year not in data[region]:
                data[region][year] = value
            else:
                data[region][year] += value
                
writer = csv.writer(sys.stdout)
writer.writerow(['region', 'year', 'value'])

for region in data:
    if region == 'all':
        for rr in range(len(config['regionorder'])):
            for year in data[region]:
                value = bundles.deltamethod_vcv.dot(data[region][year][:, rr]).dot(data[region][year][:, rr])
                writer.writerow([config['regionorder'][rr], year, value])
    else:
        for year in data[region]:
            writer.writerow([region, year, data[region][year][rr]])
