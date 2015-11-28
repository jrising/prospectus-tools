# -*- coding: utf-8 -*-
################################################################################
# Copyright 2014, Distributed Meta-Analysis System
################################################################################

"""
This file provides methods for performing operations on all of the ACP impacts.
"""

__copyright__ = "Copyright 2014, Distributed Meta-Analysis System"

__author__ = "James Rising"
__credits__ = ["James Rising"]
__maintainer__ = "James Rising"
__email__ = "jar2234@columbia.edu"

__status__ = "Production"
__version__ = "$Revision$"
# $Source$

allimpacts = ['health-mortage-0-0', 'health-mortage-1-44', 'health-mortage-45-64', 'health-mortage-65-inf', 'health-mortality', 'crime-violent', 'crime-property', 'yields-total', 'yields-maize', 'yields-wheat', 'yields-cotton', 'yields-grains', 'yields-oilcrop', 'labor-total-productivity', 'labor-low-productivity', 'labor-high-productivity', 'yields-total-noco2', 'yields-maize-noco2', 'yields-wheat-noco2', 'yields-cotton-noco2', 'yields-grains-noco2', 'yields-oilcrop-noco2', 'energy-residential']
impact_names = ["Health: Mortality (Newborns)", "Health: Mortality (Age 1 - 44)", "Health: Mortality (Age 45 - 64)", "Health: Mortality (Older than 64)", "Health: Mortality (All Ages)", "Crime: Violent Crimes", "Crime: Property Crimes", "Yields: All Crops", "Yields: Maize", "Yields: Wheat", "Yields: Cotton", "Yields: All Grains", "Yields: Soybeans", "Labor: Total Productivity", "Labor: Low-Risk Productivity", "Labor: High-Risk Productivity", "Yields: All Crops (no CO2)",  "Yields: Maize (no CO2)",  "Yields: Wheat (no CO2)",  "Yields: Cotton (no CO2)",  "Yields: All Grains (no CO2)",  "Yields: Soybeans (no CO2)", "Residential Energy Demand"]
impact_scale_units = ['people'] * 5 + ['crimes'] * 2 + ['MT'] * 6 + ['jobs'] * 3 + ['MT'] * 6 + ['%']
health_func = lambda x: 100000 * x
other_func = lambda x: 100 * (x - 1)
health_units = "additional deaths/100,000"
other_units = "% change"

# Does a high value mean that climate change has produced a bad outcome?
high_is_bad = [True] * 7 + [False] * (6 + 3 + 6 + 1)

def iterate_impacts(impacts=allimpacts):
    """Call callback(impact, impact_name, scale_units, title_units, rescale_func)."""
    for impact_ii in range(len(impacts)):
        impact = impacts[impact_ii]
        impact_name = impact_names[impact_ii]
        scale_units = impact_scale_units[impact_ii]
        if impact[0:6] == 'health':
            title_units = health_units
        else:
            title_units = other_units
        if impact[0:6] == 'health':
            rescale_func = health_func
        else:
            rescale_func = other_func

        yield (impact, impact_name, scale_units, title_units, rescale_func)

def collect_in_dictionaries(data, datum, *keys):
    for key in keys[:-1]:
        if key not in data:
            data[key] = {}
        data = data[key]

    data[keys[-1]] = datum
