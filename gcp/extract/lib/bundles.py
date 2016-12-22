# -*- coding: utf-8 -*-
################################################################################
# Copyright 2014, Distributed Meta-Analysis System
################################################################################

"""
This file provides methods for extracting data from impact bundles (.nc4 files)
"""

__copyright__ = "Copyright 2014, Distributed Meta-Analysis System"

__author__ = "James Rising"
__credits__ = ["James Rising"]
__maintainer__ = "James Rising"
__email__ = "jar2234@columbia.edu"

__status__ = "Production"
__version__ = "$Revision$"
# $Source$

import os, csv
import numpy as np
from netCDF4 import Dataset
import configs
from configs import masterregions

def read(filepath, column='rebased'):
    global masterregions

    rootgrp = Dataset(filepath, 'r', format='NETCDF4')

    years = rootgrp.variables['year'][:]
    regions = rootgrp.variables['regions'][:]
    data = rootgrp.variables[column][:, :]

    masterregions = regions

    rootgrp.close()
    
    return years, regions, data

def iterate_regions(filepath, config={}):
    """
    Config options: column
    """
    
    years, regions, data = read(filepath, config.get('column', 'rebased'))
    
    regions = list(regions)
    for region in configs.get_regions(config, regions):
        ii = regions.index(region)
        yield regions[ii], years, data[:, ii]

def iterate_values(years, values, config={}):
    """
    Config options: yearsets, years
    """
    
    if 'yearsets' in config and config['yearsets']:
        yearsets = config['yearsets']
        if yearsets == True:
            yearsets = [(2000, 2019), (2020, 2039), (2040, 2059), (2080, 2099)]
            
        for yearset in yearsets:
            yield "%d-%d" % yearset, np.mean(values[np.logical_and(years >= yearset[0], years < yearset[1])])
        return

    years = list(years)
    for year in configs.get_years(config, years):
        yield year, values[years.index(year)]
