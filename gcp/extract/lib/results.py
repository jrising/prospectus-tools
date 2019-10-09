# -*- coding: utf-8 -*-
################################################################################
# Copyright 2014, Distributed Meta-Analysis System
################################################################################

"""
This file manages the directory structures containing impact results.
"""

__copyright__ = "Copyright 2014, Distributed Meta-Analysis System"

__author__ = "James Rising"
__credits__ = ["James Rising"]
__maintainer__ = "James Rising"
__email__ = "jar2234@columbia.edu"

__status__ = "Production"
__version__ = "$Revision$"
# $Source$

import os, csv, glob, traceback
import numpy as np
import configs, bundles

rcps = ['rcp45', 'rcp85']

def iterate_targetdirs(root, targetsubdirs):
    for targetsubdir in targetsubdirs:
        if '*' in targetsubdir:
            matches = glob.glob(os.path.join(root, targetsubdir))
            matches = [match[len(root) + (0 if root[-1] == '/' else 1):] for match in matches]
            for result in iterate_targetdirs(root, matches):
                yield result
        else:
            chunks = targetsubdir.split('/')
            yield chunks + [os.path.join(root, targetsubdir)]

def iterate_both(root):
    for subdir in os.listdir(root):
        if 'batch' not in subdir and 'median' != subdir:
            continue

        for result in iterate_batch(root, subdir):
            yield result

def iterate_montecarlo(root, batches=None):
    for subdir in os.listdir(root):
        if 'batch' not in subdir:
            continue
        if batches is not None and subdir not in batches:
            continue

        for result in iterate_batch(root, subdir):
            yield result

def recurse_directories(root, levels):
    for subdir in os.listdir(root):
        if not os.path.isdir(os.path.join(root, subdir)):
            continue

        if levels == 1:
            targetdir = os.path.join(root, subdir)
            yield [subdir, targetdir]
        else:
            for recurse in recurse_directories(os.path.join(root, subdir), levels - 1):
                yield [subdir] + recurse

def iterate_batch(root, batch):
    for alldirs in recurse_directories(os.path.join(root, batch), 4):
        yield [batch] + alldirs
        
def collect_in_dictionaries(data, datum, *keys):
    for key in keys[:-1]:
        if key not in data:
            data[key] = {}
        data = data[key]

    data[keys[-1]] = datum

def directory_contains(targetdir, oneof):
    if isinstance(oneof, str):
        oneof = [oneof]

    files = os.listdir(targetdir)

    for filename in oneof:
        if filename in files:
            return True

    return False

def sum_into_data(root, basenames, columns, config, transforms, vectransforms):
    data = {} # { filestuff => { rowstuff => { batch-gcm-iam => value } } }
    years = [] # constructing years return variable here so if code doesnt execute function doesn't error
    observations = 0
    if config.get('verbose', False):
        message_on_none = "No valid target directories found"
    else:
        message_on_none = "No valid target directories found; try --verbose"

    for batch, rcp, gcm, iam, ssp, targetdir in configs.iterate_valid_targets(root, config, basenames):
        message_on_none = "No valid results sets found within directories."
        print targetdir

        # Ensure that all basenames are accounted for
        foundall = True
        for basename in basenames:
            if basename + '.nc4' not in os.listdir(targetdir):
                foundall = False
                break
        if not foundall:
            continue
    
        # Extract the values
        for ii in range(len(basenames)):
            try:
                for region, years, values in bundles.iterate_regions(os.path.join(targetdir, basenames[ii] + '.nc4'), columns[ii], config):
                    if 'region' in config.get('file-organize', []) and 'year' not in config.get('file-organize', []) and config.get('output-format', 'edfcsv') == 'valuescsv':
                        values = vectransforms[ii](values)
                        filestuff, rowstuff = configs.csv_organize(rcp, ssp, region, 'all', config)
                        if ii == 0:
                            collect_in_dictionaries(data, values, filestuff, rowstuff, (batch, gcm, iam))
                        else:
                            data[filestuff][rowstuff][(batch, gcm, iam)] += values
                        observations += 1
                        continue
                    for year, value in bundles.iterate_values(years, values, config):
                        if region == 'all':
                            value = vectransforms[ii](value)
                        else:
                            value = transforms[ii](value)
                        filestuff, rowstuff = configs.csv_organize(rcp, ssp, region, year, config)
                        if ii == 0:
                            collect_in_dictionaries(data, value, filestuff, rowstuff, (batch, gcm, iam))
                        else:
                            data[filestuff][rowstuff][(batch, gcm, iam)] += value
                        observations += 1
            except:
                print "Failed to read " + os.path.join(targetdir, basenames[ii] + '.nc4')
                traceback.print_exc()
    print "Observations:", observations
    if observations == 0:
        print message_on_none
    return data, years

def deltamethod_variance(value):
    if value.ndim == 1:
        return bundles.deltamethod_vcv.dot(value).dot(value)
    else:
        combined = np.zeros((value.shape[1]))
        for ii in range(value.shape[1]):
            combined[ii] = bundles.deltamethod_vcv.dot(value[:, ii]).dot(value[:, ii])
        return combined
