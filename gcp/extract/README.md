# Installation:

On Shackleton, download the Prospectus Tools git repository:
git clone https://github.com/jrising/prospectus-tools/

# Available scripts

The following scripts are provided, and explained in more detail below.

- single.py: Extract data from a single netCDF result file.
  Usage: `python single.py <OPTIONS> FILEPATH.nc4`

- quantiles.py: Extract quantiles across collections of results.
  Usage: `python quantiles.py CONFIG.yml <OPTIONS> <->BASENAME...`

These scripts are configurable, either from the command line (using
the syntax `--NAME=VALUE` or in a `.yml` file.  Options on the command
line override options in the configuration file.

# Using `single.py`

`single.py` extracts data from a netCDF and writes it to the standard output.

Use cases:
- Translate all of the final result across all regions and times into a CSV

  `python single.py /shares/gcp/outputs/mortality/impacts-pharaoh/single-current/rcp85/CCSM4/OECD\ Env-Growth/SSP3_v9_130325/global_interaction_gmfd.nc4`
  
- Collect the timeseries for a given county

  `python single.py --region=CAN.1.2.28 /shares/gcp/outputs/mortality/impacts-pharaoh/single-current/rcp85/CCSM4/OECD\ Env-Growth/SSP3_v9_130325/global_interaction_gmfd.nc4`
  
- Produce averages over sets of years

  `python single.py --region=CAN.1.2.28 --yearsets=yes /shares/gcp/outputs/mortality/impacts-pharaoh/single-current/rcp85/CCSM4/OECD\ Env-Growth/SSP3_v9_130325/global_interaction_gmfd.nc4`

## Using `quantiles.py`

Start by setting up a configuration file.  A few configuration files
are included in the `quantile-configs` folder.  Short comments are in
the `quantile-configs` configurations; more details are in the
[configuration documentation](config-docs.md).

Then run the quantiles script as follows:

```
python quantiles.py CONFIG.yml <OPTIONS> <->BASENAME...
```

After the configuration file comes a list (or just one) basename,
which is the name of a result file excluding the directory and the
`.nc4` suffix.  For example, if you want to extract data from all
files called "global_interaction_best.nc4", use
`global_interaction_best`.  The results from the files are summed
before being aggregated across models.  If you put a minus sign (`-`)
before the BASENAME, the result will be subtracted from the sum.

You can extract a particular region by adding an option like
`--region=...`.  In an unaggregated file, this must be the name of an
impact region.  In an aggregated file, it may be `global`, an ISO3
country, or a FUND region specified in the form FUND-XXX.  To get a
full list of the region names available in a given file, type `ncdump
-v regions FILEPATH`.

The script produces new directories under the `output-dir` specified
in the config yml file.  The division across files is specified by the `file-organize` configuration option, with RCP and SSP the default.

Use cases:
- Get a quantiles timeseries for a given region, relative to historical climate

  `python quantiles.py configs/labor.yml --region=CAN.1.2.28 labor_global_interaction_best_13dec -labor_global_interaction_best_13dec-histclim`

- Get the quantiles values for all regions over a given year span.

  `python quantiles.py configs/labor.yml --yearsets=yes labor_global_interaction_best_13dec`
