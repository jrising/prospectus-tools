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
    """Get the weights associated with models in this scenario.
    Return a dictionary of GCM -> weight
    """
    if rcp == 'truehist':
        return dict(truehist=1.0) # Degenerate case

    weights = {}

    # Read in the weights for this RCP
    with open(os.path.join('weights', rcp + 'w.csv')) as csvfp:
        reader = csv.reader(csvfp)
        for row in reader:
            weights[row[0]] = float(row[1])

    return weights

def weighted_values(values, weights):
    """Returns paired lists of results and their GCM weights.

    Args:
      values: Dictionary of GCM -> result value
      weights: Dictionary of GCM -> GCM weight
    """
    models = values.keys()
    values_list = [values[model] for model in models if model in weights]
    weights_list = [weights[model] for model in models if model in weights]

    return (values_list, weights_list)

class WeightedECDF(StepFunction):
    """Constructs a step function which is a empirical cummulative distribution function, with weighted steps."""
    def __init__(self, values, weights):
        """Takes a list of values and weights"""
        # Calculate the expected value of the distribution
        self.expected = sum(np.array(values) * np.array(weights)) / sum(weights)

        # Creat the cummulative sum that represents this ECDF
        order = sorted(range(len(values)), key=lambda ii: values[ii])
        self.values = np.array([values[ii] for ii in order])
        self.weights = [weights[ii] for ii in order]

        self.pp = np.cumsum(self.weights) / sum(self.weights)
        super(WeightedECDF, self).__init__(self.values, self.pp, sorted=True)

    def inverse(self, pp):
        """Determine the value at a given probability.
        pp may be an array of probabilities
        """
        if len(np.array(pp).shape) == 0:
            pp = np.array([pp])

        # Determine the index for interior solutions
        indexes = np.searchsorted(self.pp, pp) - 1

        useiis = indexes
        # Handle points below the lowest stp
        useiis[indexes < 0] = 0

        results = np.array(self.values[useiis], dtype=float)
        results[indexes < 0] = -np.inf

        return results
