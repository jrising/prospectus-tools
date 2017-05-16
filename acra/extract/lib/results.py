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

# The names of the RCP scenarios
rcps = ['rcp26', 'rcp45', 'rcp60', 'rcp85']

def make_pval_file(targetdir, pvals):
    """Create a file to contain the quantile information."""
    with os.fdopen(os.open(os.path.join(targetdir, "pvals.txt"), os.O_WRONLY | os.O_CREAT | os.O_EXCL), 'w') as fp:
        for key in pvals:
            fp.write(key + ":\t" + str(pvals[key]) + "\n")

def read_pval_file(targetdir):
    """Read the quantile information from a file."""
    with open(os.path.join(targetdir, "pvals.txt"), 'r') as fp:
        pvals = {}
        for line in fp:
            parts = line.split("\t") # formated as "key:\tvalue"
            try:
                pvals[parts[0][0:-1]] = float(parts[1])
            except:
                pvals[parts[0][0:-1]] = parts[1]

    return pvals

def iterate(root):
    """Iterator through all results under a given root directory."""
    iterate_montecarlo(root)
    iterate_byp(root)

def iterate_montecarlo(root, batches=None, presuffix=False):
    """Iterator through all Monte Carlo results under a given root directory."""
    # If truehist is request, only return this scenario
    if batches == 'truehist':
        # Look for batches under root
        batches = os.listdir(root)

        for batch in batches:
            if batch[0:6] != 'batch-':
                continue

            # Point to the truehist scenario
            targetdir = os.path.join(root, batch, 'truehist')
            if not os.path.exists(targetdir) or 'pvals.txt' not in os.listdir(targetdir):
                continue # Only consider results with pvals

            # Return all result set information
            pvals = read_pval_file(targetdir)

            yield (batch, 'truehist', 'truehist', 'truehist', pvals, targetdir)

        return

    if batches is None:
        # Iterate through all batches
        batches = os.listdir(root)

        for batch in batches:
            if batch[0:5] != 'batch':
                continue

            # Results returned by iterate_batch
            for result in iterate_batch(root, batch):
                yield result

    else:
        ## batches should be sequence of numbers
        for batchnum in batches:
            if os.path.exists(os.path.join(root, str(batchnum))):
                batch = batchnum
            else:
                batch = 'batch-' + str(batchnum)
                if not os.path.exists(os.path.join(root, batch)):
                    continue

            # Results returned by iterate_batch
            for result in iterate_batch(root, batch):
                yield result

def iterate_byp(root, batches=None):
    """Iterator through all constant-quantile results under a given root directory."""
    # The quantile value used by each named directory
    pdirs = dict(pmed=.5, plow=.33333, phigh=.66667)

    if batches == 'truehist':
        # If the truehist scenario is request, only look for this
        for pdir in pdirs.keys():
            targetdir = os.path.join(root, pdir, 'truehist')
            if not os.path.exists(targetdir) or 'pvals.txt' not in os.listdir(targetdir):
                continue # Ignore if no pval file

            # Yield the result set information
            pvals = read_pval_file(targetdir)

            yield (pdir, 'truehist', 'truehist', 'truehist', pvals, targetdir)

        return

    # Look only for the named directories
    for pdir in pdirs.keys():
        if not os.path.exists(os.path.join(root, pdir)):
            continue

        # Results returned by iterate_batch
        for result in iterate_batch(root, pdir):
            yield result

def iterate_batch(root, batch):
    """Find result, in a tree of the form <root>/<batch>/<rcp>/<model>/<realization>/<results>."""
    for rcp in os.listdir(os.path.join(root, batch)):
        try:
            for model in os.listdir(os.path.join(root, batch, rcp)):
                try:
                    for realization in os.listdir(os.path.join(root, batch, rcp, model)):
                        targetdir = os.path.join(root, batch, rcp, model, realization)
                        if 'pvals.txt' not in os.listdir(targetdir):
                            continue # Skip if no pvals information

                        # Return all the rest of the information
                        pvals = read_pval_file(targetdir)

                        yield (batch, rcp, model, realization, pvals, targetdir)
                except OSError:
                        continue
        except OSError:
            continue


def directory_contains(targetdir, oneof):
    """Check if a target directory contains at least one of the list of files."""
    files = os.listdir(targetdir)

    for filename in oneof:
        if filename in files:
            return True # We found one!

    return False
