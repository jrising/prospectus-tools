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

import os, csv, glob

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
