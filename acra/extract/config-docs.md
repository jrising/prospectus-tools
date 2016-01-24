# File organization options

## `results-root`

Directory containing the impacts results tree

## `output-dir`

Directory to write output quantile files

# Top-level configuration

## `level` (options: county, state, region, or national)

Aggregation level.

## `do-montecarlo` (options: yes or no)

Calculate values over the Monte Carlo results?

## `do-adaptation` (options: no, yes, or comparison)

Calculate adaptation results

# Year handling

## `do-yearsets` (options: yes or no)

Collect results into sets of years?

## `do-yearsetmeans` (options: yes or no)

Report the mean of these sets of years?

# Limiting the universe of results

## `only-rcp` (options: null, rcp26, rcp45, rcp60, or rcp85)

Perform operations for only one RCP or realization?  Set to `null` for all RCPs.

## `only-realization` (options: null, or a realization name)

For results that include a realization, either `null` or a single realization number, e.g., `001`

## `only-impacts` (options: all, or a list like `[health-mortality, yields-maize]`

Which impacts should be included?  List or all

## `allow-partial` (integer)

Include results without a full set of models?
Specify the least models to allow, or 0 to require all

## `checks` (options: null or list of files)

Files to check within impact directories

## `batches` (integer)

Number of batches to include.
For ACP, county levels 5, state and region had 10, national had 25

# Reading the results

## `column` (integer)

Which column to read from the files (starting from 2, the final result)

# Combining results

## `do-gcmweights` (default: `yes`)

In constructing an empirical distribution, should GCMs be weighted
according to the weights in the ACP?  If you want to produce
unweighted results or use models that are not in the ACP weights, set
this to 'no'.

# Outputing results

## `output-format` (default: `edfcsv`)

How should the output file be formatted and what information should it
contain?  The options are:

* `edfcsv`: Percentiles describing an empirical distribution function
of the values.  There is one row for each region at the specified
aggregation level (see `level`), and a column for each percentile from
1 to 99.
* `valuescsv`: All values that would go into forming an empirical distribution as described under `edfcsf`.  There is a row for each value within each region, and its corresponding weight.

