# File organization options

## `results-root`

Directory containing the impacts results tree.  To do a Monte Carlo
run (see `do-montecarlo`), this directory should contain directories
named `batch-0`, `batch-1`, and so on.  To do a constant p-value run,
or a single batch from a Monte Carlo run, this directory should end
with the batch directory itself (and should contain RCP directories).

## `output-dir`

Directory to write output quantile files.

## `output-file`

Alternative to `output-dir`, where all results are always written to a
single file.

## `file-organize` (subset of rcp, ssp, region, year)

For which unique variables should distinct files be made?  The
remaining values will be used to identify rows.

## `suffix`

A suffix on the filnames produced.  For example, if a default filename would be `rcp85-SSP3_v9_130325.csv`, then specifying `--suffix=-latest` on the command-line would produce the file `rcp85-SSP3_v9_130325-latest.csv`.

# Top-level configuration

## `do-montecarlo` (options: yes or no)

Calculate values over the Monte Carlo results?

## `deltamethod` (options: yes, no, or a deltamethod root directory)

If deltamethod is yes, the directory is taken to be a directory of
deltamethod variances; if it's a directory, a parallel deltamethod
run is performed, where the directory structure is taken to be
parallel to the normal results structure, and the variances there are
used to produce a full distribution over results.

# Year handling

## `yearsets` (options: yes, no, or list of start-end tuples)

Should the results be reported as the average across spans of years?

## `years` (options: null or list of years)

Only extract results for the given years, if provided.

# Region handling

## `regions` (options: null or list of regions)

Only extract results for the given regions, if provided

# Limiting the universe of results

## `only-rcp` (options: null, rcp26, rcp45, rcp60, or rcp85)

Perform operations for only one RCP or realization?  Set to `null` for all RCPs.

## `only-iam` (options: null, low, high)

Perform operations for only one IAM (high or low)?  Set to `null` for all RCPs.

## `only-models` (options: all (default), or list

Only include certain climate models in the results.  e.g., `[hadgem2-ao, hadgem2-es]`.

## `checks` (options: null or list of files)

Files to check within impact directories

# Reading the results

## `column` (string)

Which column to read from the files (default is `rebased`, the final result)

# Combining results

## `do-gcmweights` (default: `yes`)

In constructing an empirical distribution, should GCMs be weighted
according to the weights in the ACP?  If you want to produce
unweighted results or use models that are not in the ACP weights, set
this to 'no'.

# Outputing results

## `evalqvals` (default: [.17, .5, .83])

The quantiles to report when output-format is edfcsv.

## `output-format` (default: `edfcsv`)

How should the output file be formatted and what information should it
contain?  The options are:

* `edfcsv`: Percentiles describing an empirical distribution function
of the values.  There is one row for each region and a column for
percentiles of 17%, 50%, and 83%.
* `valuescsv`: All values that would go into forming an empirical distribution as described under `edfcsf`.  There is a row for each value within each region, and its corresponding weight.

