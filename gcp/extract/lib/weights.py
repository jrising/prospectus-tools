# -*- coding: utf-8 -*-
################################################################################
# Copyright 2014, Distributed Meta-Analysis System
################################################################################

"""
This file provides methods for handling weighting across impacts.
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
from statsmodels.distributions.empirical_distribution import StepFunction

def get_weights(rcp):
    weights = get_weights_april2016(rcp)
    weights.update(get_weights_march2018(rcp))

    return weights

def get_weights_april2016(rcp):
    weights = {}

    with open('/shares/gcp/climate/BCSD/SMME/SMME-weights/' + rcp + '_2090_SMME_edited_for_April_2016.tsv', 'rU') as tsvfp:
        reader = csv.reader(tsvfp, delimiter='\t')
        header = reader.next()
        for row in reader:
            model = row[1].split('_')[0].strip('*').lower()
            weight = float(row[2])
            weights[model] = weight

    if rcp == 'rcp45':
        weights["pattern4"] = 0 # Explicitly remove (so no messages)

    return weights

def get_weights_march2018(rcp):
    weights = {}

    with open('/shares/gcp/climate/BCSD/SMME/SMME-weights/' + rcp + '_SMME_weights.tsv', 'rU') as tsvfp:
        reader = csv.reader(tsvfp, delimiter='\t')
        header = reader.next()
        for row in reader:
            model = row[1].strip('*').lower()
            if '_' in model:
                model = 'surrogate_' + model
            weight = float(row[2])
            weights[model] = weight

    if rcp == 'rcp45':
        weights["surrogate_gfdl-esm2g_06"] = 0 # Explicitly remove (so no messages)
            
    return weights

def weighted_values(values, weights):
    """Takes a dictionary of model => value"""
    models = values.keys()
    values_list = [values[model] for model in models if model in weights]
    weights_list = [weights[model] for model in models if model in weights]

    return (values_list, weights_list)

class WeightedECDF(StepFunction):
    def __init__(self, values, weights, ignore_missing=False):
        """Takes a list of values and weights"""
        if ignore_missing:
            values = np.array(values)
            weights = np.array(weights)
            weights[np.isnan(values)] = 0
            values[np.isnan(values)] = 0
            if np.sum(weights) == 0 and len(weights) > 0:
                weights[0] = 1
                values[0] = np.nan
        
        self.expected = sum(np.array(values) * np.array(weights)) / sum(weights)

        order = sorted(range(len(values)), key=lambda ii: values[ii])
        self.values = np.array([values[ii] for ii in order])
        self.weights = [weights[ii] for ii in order]

        self.pp = np.cumsum(self.weights) / sum(self.weights)
        super(WeightedECDF, self).__init__(self.values, self.pp, sorted=True)

    def inverse(self, pp):
        if len(np.array(pp).shape) == 0:
            pp = np.array([pp])

        indexes = np.searchsorted(self.pp, pp) - 1

        useiis = indexes
        useiis[indexes < 0] = 0

        results = np.array(self.values[useiis], dtype=float)
        results[indexes < 0] = -np.inf

        # Special case with identical weights
        if .5 in pp and np.all(np.array(self.weights) == self.weights[0]):
            results[pp.index(.5)] = np.median(self.values)
        if 2 in pp: # Calculate mean
            results[pp.index(2)] = np.average(self.values, weights=self.weights)
        if 3 in pp:
            mu = np.average(self.values, weights=self.weights)
            results[pp.index(3)] = np.sqrt(np.sum(self.weights * (self.values - mu)**2) / np.sum(self.weights))

        return results

    @staticmethod
    def encode_evalqvals(evalqvals):
        encoder = {'mean': 2, 'sdev': 3}
        return map(lambda p: p if isinstance(p, float) else encoder[p], evalqvals)

if __name__ == '__main__':
    import sys
    
    batchdir = sys.argv[1]

    for rcp in os.listdir(batchdir):
        if rcp == 'historical':
            continue
        weights = get_weights(rcp)
        print weights
        for gcm in os.listdir(os.path.join(batchdir, rcp)):
            try:
                print gcm, weights[gcm.lower()]
            except:
                print "Cannot find weight for %s under %s" % (gcm, rcp)
