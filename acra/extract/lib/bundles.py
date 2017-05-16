# -*- coding: utf-8 -*-
################################################################################
# Copyright 2014, Distributed Meta-Analysis System
################################################################################

"""
This file provides methods for extracting data from impact bundles (.csv.gz files).
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

def get_yearses(fp, yearses):
    """Get the given years of results, for collections of year sets."""
    if yearses[0][0] < 1000:
        # Just head and tail or tail of results
        reader = csv.reader(fp)
        reader.next()
        values = [float(row[1]) for row in reader]

        # Return a list of all requested subsets
        results = []
        for years in yearses:
            if years[0] > 0:
                results.append(values[years[0]:years[1]])
            elif years[1] == 0:
                results.append(values[years[0]:])
            else:
                results.append(values[years[0]:years[1]])

        return results

    # Create a list of results
    results = []
    reader = csv.reader(fp) # Read the results

    yearses_ii = 0
    found = False
    values = []
    for row in reader:
        if not found: # We are still looking for the start of this year-set
            try:
                if int(row[0]) >= yearses[yearses_ii][0]:
                    found = True # We found it
            except:
                pass

        if found: # Add on this values
            if row[1] != 'NA':
                values.append(float(row[1]))
            if int(row[0]) == yearses[yearses_ii][1]: # That's the last year of this set
                found = False
                results.append(values)
                values = []
                yearses_ii += 1

    if found: # If there are any left over results
        results.append(values)

    return results

def get_years(fp, years, column=2):
    """Return the results for the given years, as specifically requested years."""
    results = []
    reader = csv.reader(fp)
    reader.next()

    years_ii = 0 # Start by looking for the first year
    for row in reader:
        # Oops, we're asking for a year outside of the range
        while years_ii < len(years) and int(row[0]) > years[years_ii]:
            results.append(None)
            years_ii += 1

        # We have no more years to collect
        if years_ii == len(years):
            break

        # Look for the given year
        if int(row[0]) == years[years_ii]:
            if row[column-1] != 'NA':
                results.append(float(row[column-1]))
            else:
                results.append(None)
            years_ii += 1
        else:
            results.append(None) # row[0] < year

    return results

def iterate_bundle(targetdir, impact, suffix, working_suffix=''):
    """Yield a file pointer to each file in the given result bundle."""

    # Create a working directory to extract into
    if os.path.exists('working' + working_suffix):
        os.system('rm -r working' + working_suffix)
    os.mkdir('working' + working_suffix)
    os.chdir('working' + working_suffix)
    os.system("tar -xzf " + os.path.join(targetdir, impact + suffix + ".tar.gz"))
    os.chdir('..')

    impactdir = os.path.join('working' + working_suffix, impact + suffix)
    if os.path.exists(impactdir):
        # Go through all region files
        for name in os.listdir(impactdir):
            if name == impact:
                continue # just the directory

            region = name[0:-4]

            # Open this result and produce it
            with open(os.path.join('working' + working_suffix, impact + suffix, name)) as fp:
                yield (region, fp)

    # Remove the working directory
    os.system('rm -r working' + working_suffix)
