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

import os, csv, glob, traceback, re
import numpy as np
import configs, bundles

debug = True
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

def subdirs(root):
    if isinstance(root, dict):
        subdirs = None
        for name in root:
            mydirs = os.listdir(root[name])
            if subdirs is None: # Not initialized yet
                subdirs = mydirs
            else:
                subdirs = subdirs & mydirs
        return subdirs

    return os.listdir(root)
                
def iterate_both(root):
    for subdir in subdirs(root):
        if 'batch' not in subdir and 'median' != subdir:
            continue

        for result in iterate_batch(root, subdir):
            yield result

def iterate_montecarlo(root, batches=None):
    for subdir in subdirs(root):
        if 'batch' not in subdir:
            continue
        if batches is not None and subdir not in batches:
            continue

        for result in iterate_batch(root, subdir):
            yield result

def recurse_directories(root, levels):
    if isinstance(root, dict):
        subdirs = None
        for name in root:
            mydirs = set(os.path.join(*elements[:-1]) for elements in recurse_directories(root[name], levels))
            if subdirs is None: # Not initialized yet
                subdirs = mydirs
            else:
                subdirs = subdirs & mydirs
        for elements in subdirs:
            yield elements.split('/') + [{name: os.path.join(root[name], elements) for name in root}]
        return
    
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
    if isinstance(root, dict):
        subdir = {name: os.path.join(root[name], batch) for name in root}
    else:
        subdir = os.path.join(root, batch)
    for alldirs in recurse_directories(subdir, 4):
        yield [batch] + alldirs
        
def collect_in_dictionaries(data, datum, *keys):
    for key in keys[:-1]:
        if key not in data:
            data[key] = {}
        data = data[key]

    data[keys[-1]] = datum

def directory_contains(targetdir, oneof, bypattern=False):
    if isinstance(targetdir, dict):
        for name in targetdir:
            if bypattern and isinstance(oneof, str) and not re.match(name, oneof):
                continue
            if not directory_contains(targetdir[name], oneof):
                return False
        return True
    
    if isinstance(oneof, str):
        oneof = [oneof]

    files = os.listdir(targetdir)

    for filename in oneof:
        if filename in files:
            return True

    return False

def sum_into_data(root, basenames, columns, config, transforms, vectransforms):
    data = {} # { filestuff => { rowstuff => { batch-gcm-iam => value } } }

    observations = 0
    if config.get('verbose', False):
        message_on_none = "No valid target directories found"
    else:
        message_on_none = "No valid target directories found; try --verbose"

    for batch, rcp, gcm, iam, ssp, targetdir in configs.iterate_valid_targets(root, config, basenames):
        message_on_none = "No valid results sets found within directories."
        if isinstance(targetdir, str):
            print targetdir

        # Ensure that all basenames are accounted for
        foundall = True
        for basename in basenames:
            if not directory_contains(targetdir, basename + '.nc4', bypattern=True):
                foundall = False
                break
        if not foundall:
            continue

        # Extract the values
        for ii in range(len(basenames)):
            if isinstance(targetdir, dict):
                fullpath = os.path.join(configs.multipath(targetdir, basenames[ii]),  basenames[ii] + '.nc4')
            else:
                fullpath = os.path.join(targetdir, basenames[ii] + '.nc4')
            
            try:
                for region, years, values in bundles.iterate_regions(fullpath, columns[ii], config):
                    if 'region' in config.get('file-organize', []) and 'year' not in config.get('file-organize', []) and output_format == 'valuescsv':
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
                print "Failed to read " + fullpath
                traceback.print_exc()
                if debug:
                    exit()

    print "Observations:", observations
    if observations == 0:
        print message_on_none

    return data

def deltamethod_variance(value, config):
    if config.get('multiimpact_vcv', None) is None:
        deltamethod_vcv = bundles.deltamethod_vcv
    else:
        deltamethod_vcv = config['multiimpact_vcv']
        
    if value.ndim == 1:
        return deltamethod_vcv.dot(value).dot(value)
    else:
        combined = np.zeros((value.shape[1]))
        for ii in range(value.shape[1]):
            combined[ii] = deltamethod_vcv.dot(value[:, ii]).dot(value[:, ii])
        return combined
