# -*- coding: utf-8 -*-
################################################################################
# Copyright 2014, Distributed Meta-Analysis System
################################################################################

"""
This file provides methods for handling weighting across GCMs under
delta method calculations.
"""

__copyright__ = "Copyright 2014, Distributed Meta-Analysis System"

__author__ = "James Rising"
__credits__ = ["James Rising"]
__maintainer__ = "James Rising"
__email__ = "j.a.rising@lse.ac.uk"

__status__ = "Production"
__version__ = "$Revision$"
# $Source$

import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm

class WeightedGMCDF(object):
    """
    A weighted Gaussian mixture model.
    """
    def __init__(self, means, variances, weights):
        self.means = means
        self.sds = np.sqrt(variances) # as std. dev.
        self.weights = weights / np.sum(weights) # as fractions of 1

    def inverse(self, pp):
        # pp is a scalar or vector of probabilities
        # make it an array, if not already
        if len(np.array(pp).shape) == 0:
            pp = np.array([pp])

        # determine extreme left and right bounds for root-finding
        pp = np.array(pp) # needs to be np array
        left = np.min(norm.ppf(np.min(pp), self.means, self.sds))
        right = np.max(norm.ppf(np.max(pp[pp < 1]), self.means, self.sds))
        # find root for each probability
        roots = []
        for p in pp:
            if p == 2:
                roots.append(np.average(self.means, weights=self.weights))
                continue

            # Set up mixed distribution CDF with root and find it
            func = lambda x: sum(self.weights * norm.cdf(x, self.means, self.sds)) - p
            try:
                roots.append(brentq(func, left, right))
            except:
                print "Cannot find the location of %f for the following means and std. devs:" % p
                print self.means
                print self.sds
                roots.append(np.nan)

        return roots

    @staticmethod
    def encode_evalqvals(evalqvals):
        encoder = {'mean': 2}
        return map(lambda p: p if isinstance(p, float) else encoder[p], evalqvals)

if __name__ == '__main__':
    ## Example between R and python
    ## R:
    # means <- rnorm(10)
    # sds <- rexp(10)
    # weights <- runif(10)
    # weights <- weights / sum(weights)
    # draws <- sapply(1:100000, function(ii) sample(rnorm(10, means, sds), 1, prob=weights))
    # pp <- runif(10)
    # quantile(draws, pp)
    ## For the values below:
    # > quantile(draws, pp)
    #  4.261865%   57.54305%   9.961645%    13.1325%    68.3729%   89.93871%   37.68216%   25.06827%    72.6134%   92.35501% 
    # -2.70958468  0.77240194 -2.15403320 -1.90146370  1.17428553  1.95475922 -0.06482985 -0.92293638  1.36865349  2.00405179 
    
    ## Python:
    means = [-1.10402809, 1.91300947, -2.21007153, 0.65175650, 0.56314868, -0.28337581, 0.98788803, 1.10211432, -0.06220629, -1.45807086]
    variances = np.array([0.65422226, 0.13413332, 0.61493262, 0.29639041, 2.20748648, 1.69513869, 1.15008972, 0.41550756, 0.03384455, 1.07446232])**2
    weights = [0.07420341, 0.16907337, 0.11439943, 0.08439015, 0.01868190, 0.14571485, 0.07630478, 0.17063990, 0.09951820, 0.04707401]
    pp = [0.04261865, 0.57543051, 0.09961645, 0.13132502, 0.68372897, 0.89938713, 0.37682157, 0.25068274, 0.72613404, 0.92355014]
    
    dist = WeightedGMCDF(means, variances, weights)
    print dist.inverse(pp)
    # [-2.708582712985005, 0.7720415676939508, -2.152969315647189, -1.8999500392063315, 1.1698917665106159, 1.955783738182657, -0.0641650435162273, -0.9150700927430755, 1.3660161904436894, 2.004650382993468]
