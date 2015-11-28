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

import os, csv

rcps = ['rcp26', 'rcp45', 'rcp60', 'rcp85']

def make_pval_file(targetdir, pvals):
    with os.fdopen(os.open(os.path.join(targetdir, "pvals.txt"), os.O_WRONLY | os.O_CREAT | os.O_EXCL), 'w') as fp:
        for key in pvals:
            fp.write(key + ":\t" + str(pvals[key]) + "\n")

def read_pval_file(targetdir):
    with open(os.path.join(targetdir, "pvals.txt"), 'r') as fp:
        pvals = {}
        for line in fp:
            parts = line.split("\t")
            try:
                pvals[parts[0][0:-1]] = float(parts[1])
            except:
                pvals[parts[0][0:-1]] = parts[1]

    return pvals

def iterate(root):
    iterate_montecarlo(root)
    iterate_byp(root)

def iterate_montecarlo(root, batches=None):
    if batches == 'truehist':
        batches = os.listdir(root)

        for batch in batches:
            if batch[0:6] != 'batch-':
                continue

            targetdir = os.path.join(root, batch, 'truehist')
            if not os.path.exists(targetdir) or 'pvals.txt' not in os.listdir(targetdir):
                continue

            pvals = read_pval_file(targetdir)

            yield (batch, 'truehist', 'truehist', 'truehist', pvals, targetdir)

        return

    ## batches should be sequence of numbers
    if batches is None:
        batches = os.listdir(root)

        for batch in batches:
            if batch[0:5] != 'batch':
                continue

            for result in iterate_batch(root, batch):
                yield result

    else:
        for batchnum in batches:
            if os.path.exists(os.path.join(root, str(batchnum))):
                batch = batchnum
            else:
                batch = 'batch-' + str(batchnum)
                if not os.path.exists(os.path.join(root, batch)):
                    continue

            for result in iterate_batch(root, batch):
                yield result

def iterate_byp(root, batches=None):
    pdirs = dict(pmed=.5, plow=.33333, phigh=.66667)

    if batches == 'truehist':
        for pdir in pdirs.keys():
            targetdir = os.path.join(root, pdir, 'truehist')
            if not os.path.exists(targetdir) or 'pvals.txt' not in os.listdir(targetdir):
                continue

            pvals = read_pval_file(targetdir)

            yield (pdir, 'truehist', 'truehist', 'truehist', pvals, targetdir)

        return

    for pdir in pdirs.keys():
        if not os.path.exists(os.path.join(root, pdir)):
            continue

        for result in iterate_batch(root, pdir):
            yield result

def iterate_batch(root, batch):
    for rcp in os.listdir(os.path.join(root, batch)):
        try:
            for model in os.listdir(os.path.join(root, batch, rcp)):
                try:
                    for realization in os.listdir(os.path.join(root, batch, rcp, model)):
                        targetdir = os.path.join(root, batch, rcp, model, realization)
                        if 'pvals.txt' not in os.listdir(targetdir):
                            continue

                        pvals = read_pval_file(targetdir)

                        yield (batch, rcp, model, realization, pvals, targetdir)
                except OSError:
                        continue
        except OSError:
            continue
            

def directory_contains(targetdir, oneof):
    files = os.listdir(targetdir)

    for filename in oneof:
        if filename in files:
            return True

    return False
