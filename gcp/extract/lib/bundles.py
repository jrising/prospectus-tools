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

def read(filepath, column='rebased'):
    rootgrp = Dataset(filepath, 'r', format='NETCDF4')

    years = rootgrp.variables['years'][:]
    regions = rootgrp.variables['regions'][:]
    data = rootgrp.variables[column][:, :]

    rootgrp.close()
    
    return years, regions, data

def iterate_regions(filepath, config={}):
    """
    Config options: column
    """
    
    years, regions, data = read(filepath, config.get('column', 'rebased'))

    for region in get_regions(config, regions):
        ii = regions.index(region)
        yield regions[ii], years, reader.variables[column][:, ii]

def iterate_values(years, values, config={}):
    """
    Config options: yearsets, years
    """
    
    if 'yearsets' in config and config['yearsets']:
        yearsets = config['yearsets']
        if yearsets == True:
            yearsets = [(2000, 2019), (2020, 2039), (2040, 2059), (2080, 2099)]
            
        for yearset in yearsets:
            yield "%d-%d" % yearset, np.mean(values[years >= yearset[0] and years < yearset[1]])
        return

    for year in configs.get_years(config, years):
        yield years, values[years == year]
