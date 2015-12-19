## Using `single.sh`

The `single.sh` script produces a set of climate impact results from a single climate realization.  The climate realization should consist of NetCDF files for precipitation and daily mean, maximum, and minimum temperature.  The impact results will consist of effects for crime, mortality, yields, energy, and labor productivity.

The `single.sh` script must be run on a server where DMAS is installed locally, with all of the associated ACP results.  Shackleton is such a server.

The syntax for `single.sh` is:
```
./single.sh [weather path] <scenario> <q-value>
```

 - `[weather path]` is the path to a directory whose sub-directories contain a single NetCDF file for each of the following:
   - Precipitation (filename contains `pr`)
   - Mean temperature (filename contains `tas`)
   - Maximum temperature (filename contains `tasmax`)
   - Minimum temperature (filename contains `taxmin`)
 - `<scenario>` is an optional scenario from the set `rcp26`, `rcp45`, `rcp60`, `rcp85`, or nothing (`""`).  Default is `rcp85`.
 - `<q-value>` is an optional quantile for the economic damage function, between 0 and 1.  Only used if `<scenario>` is given.  Default is 0.5.

The results are in files named:
- `<impact>-national.tar.gz`: The nationally aggregated results
- `<impact>-state.tar.gz`: The state aggregated results
- `<impact>.tar.gz`: The county-specific results

Each `.tar.gz` file has one or more `.csv` files with an impact for
each year.  Typically this will consist of three columns: the year,
the impact relative to 2012, and the raw impact value.

Definitions of the values are as follows:

- `health-mortage-0-0`: Health: Mortality, Newborns (deaths per person)
- `health-mortage-1-44`: Health: Mortality, Age 1 - 44 (deaths per person)
- `health-mortage-45-64`: Health: Mortality, Age 45 - 64 (deaths per person)
- `health-mortage-65-inf`: Health: Mortality, Older than 64 (deaths per person)
- `health-mortality`: Health: Mortality, All Ages (deaths per person)
- `crime-violent`: Crime: Violent Crimes (fractional change in crimes)
- `crime-property`: Crime: Property Crimes (fractional change in crimes)
- `yields-total`: Yields: All Crops (fractional change in MT)
- `yields-maize`: Yields: Maize (fractional change in MT)
- `yields-wheat`: Yields: Wheat (fractional change in MT)
- `yields-cotton`: Yields: Cotton (fractional change in MT)
- `yields-grains`: Yields: All Grains (fractional change in MT)
- `yields-oilcrop`: Yields: Soybeans (fractional change in MT)
- `yields-total-noco2`: Yields: All Crops, no CO2 (fractional change in MT)
- `yields-maize-noco2`: "Yields: Maize, no CO2 (fractional change in MT)
- `yields-wheat-noco2`: "Yields: Wheat, no CO2 (fractional change in MT)
- `yields-cotton-noco2`: "Yields: Cotton, no CO2 (fractional change in MT)
- `yields-grains-noco2`: "Yields: All Grains, no CO2 (fractional change in MT)
- `yields-oilcrop-noco2`: "Yields: Soybeans, no CO2 (fractional change in MT)
- `labor-total-productivity`: Labor: Total Productivity (fractional change in worker-equivalents)
- `labor-low-productivity`: Labor: Low-Risk Productivity (fractional change in worker-equivalents)
- `labor-high-productivity`: Labor: High-Risk Productivity (fractional change in worker-equivalents)
- `energy-residential`: Residential Energy Demand (fractional change in demand)

