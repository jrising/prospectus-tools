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
    if yearses[0][0] < 1000:
        # Just heads and tails
        reader = csv.reader(fp)
        reader.next()
        values = [float(row[1]) for row in reader]

        results = []
        for years in yearses:
            if years[0] > 0:
                results.append(values[years[0]:years[1]])
            elif years[1] == 0:
                results.append(values[years[0]:])
            else:
                results.append(values[years[0]:years[1]])

        return results

    results = []
    reader = csv.reader(fp)

    yearses_ii = 0
    found = False
    values = []
    for row in reader:
        if not found:
            try:
                if int(row[0]) >= yearses[yearses_ii][0]:
                    found = True
            except:
                pass

        if found:
            if row[1] != 'NA':
                values.append(float(row[1]))
            if int(row[0]) == yearses[yearses_ii][1]:
                found = False
                results.append(values)
                values = []
                yearses_ii += 1

    if found:
        results.append(values)

    return results

def get_years(fp, years, column=2):
    results = []
    reader = csv.reader(fp)
    reader.next()

    years_ii = 0
    for row in reader:
        while years_ii < len(years) and int(row[0]) > years[years_ii]:
            results.append(None)
            years_ii += 1

        if years_ii == len(years):
            break

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
    if os.path.exists('working' + working_suffix):
        os.system('rm -r working' + working_suffix)
    os.mkdir('working' + working_suffix)
    os.chdir('working' + working_suffix)
    os.system("tar -xzf " + os.path.join(targetdir, impact + suffix + ".tar.gz"))
    os.chdir('..')

    for name in os.listdir(os.path.join('working' + working_suffix, impact + suffix)):
        if name == impact:
            continue # just the directory

        region = name[0:-4]

        with open(os.path.join('working' + working_suffix, impact + suffix, name)) as fp:
            yield (region, fp)

    os.system('rm -r working' + working_suffix)
