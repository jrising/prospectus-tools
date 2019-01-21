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

deltamethod_vcv = None

def read(filepath, column='rebased', deltamethod=False):
    global deltamethod_vcv

    try:
        rootgrp = Dataset(filepath, 'r', format='NETCDF4')
    except:
        print "Error: Cannot read %s" % filepath
        exit()

    years = rootgrp.variables['year'][:]
    regions = rootgrp.variables['regions'][:]

    if deltamethod is None:
        # Infer from the file
        deltamethod = 'vcv' in rootgrp.variables
        
    if deltamethod:
        data = rootgrp.variables[column + '_bcde'][:, :, :]
        if deltamethod_vcv is None:
            deltamethod_vcv = rootgrp.variables['vcv'][:, :]
        else:
            assert(np.all(deltamethod_vcv == rootgrp.variables['vcv'][:, :]))
    else:
        data = rootgrp.variables[column][:, :]

    rootgrp.close()

    # Correct bad regions in costs
    if filepath[-10:] == '-costs.nc4' and not isinstance(regions[0], str) and not isinstance(regions[0], unicode) and np.isnan(regions[0]):
        rootgrp = Dataset(filepath.replace('-costs.nc4', '.nc4'), 'r', format='NETCDF4')
        regions = rootgrp.variables['regions'][:]
        rootgrp.close()

    return years, regions, data

def iterate_regions(filepath, column, config={}):
    if column is not None or 'costs' not in filepath:
        years, regions, data = read(filepath, column if column is not None else 'rebased', config.get('deltamethod', None))
    else:
        years, regions, data1 = read(filepath, 'costs_lb', config.get('deltamethod', None))
        years, regions, data2 = read(filepath, 'costs_ub', config.get('deltamethod', None))
        data = ((data1 + data2) / 2) / 1e5

    if deltamethod_vcv is not None:
        ## Inferred that these were deltamethod files
        config['deltamethod'] = True
    config['regionorder'] = list(regions)

    if configs.is_allregions(config):
        yield 'all', years, data
        return

    regions = list(regions)
    for region in configs.get_regions(config, regions):
        if region == 'global':
            region = ''
        ii = regions.index(region)
        if config.get('deltamethod', False):
            yield regions[ii], years, data[:, :, ii]
        else:
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
            if isinstance(yearset, list):
                yearset = tuple(yearset)
            if config.get('deltamethod', False):
                if values.ndim == 1:
                    yield "%d-%d" % yearset, np.mean(values[:, np.logical_and(years >= yearset[0], years < yearset[1])], axis=1)
                else: # multiple regions included
                    yield "%d-%d" % yearset, np.mean(values[:, np.logical_and(years >= yearset[0], years < yearset[1]), :], axis=1)
            else:
                if values.ndim == 1:
                    yield "%d-%d" % yearset, np.mean(values[np.logical_and(years >= yearset[0], years < yearset[1])])
                else: # multiple regions included
                    yield "%d-%d" % yearset, np.mean(values[np.logical_and(years >= yearset[0], years < yearset[1]), :], axis=0)
        return

    years = list(years)
    for year in configs.get_years(config, years):
        if config.get('deltamethod', False):
            if values.ndim == 2:
                yield year, values[:, years.index(year)]
            else:
                yield year, values[:, years.index(year), :]
        else:
            if values.ndim == 1:
                yield year, values[years.index(year)]
            else:
                yield year, values[years.index(year), :]
