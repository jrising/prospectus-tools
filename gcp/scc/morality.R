### Configuration: Fill in the values below

setwd("~/research/gcp/prospectus-tools/gcp/scc")
source("cost-damagefunc.R")

## Look for all input files of this form
filetemplate <- "jan2018/global_damages_RCP_SSP.csv"
## They must have the following columns:
## - year
## - gcm: GCM name
## - mod: IAM name (high or low)
## - <tascol>: The global temperature, using the column name below
## - <impcol>: The global impact, using the column name below
tascol <- "global_tas"
impcols <- c("damages_lifeyears_COSTS_vly_epa_scaled", "damages_lifeyears_COSTS_vly_epa_popavg", "damages_lifeyears_COSTS_vly_ag02_scaled", "damages_lifeyears_COSTS_vly_ag02_popavg") #c("damages_deaths_COSTS_vsl_epa_scaled", "damages_deaths_COSTS_vsl_epa_popavg", "damages_deaths_COSTS_vsl_ag02_scaled", "damages_deaths_COSTS_vsl_ag02_popavg")
prefixs <- c("vly-epa-scaled", "vly-epa-popavg", "vly-ag02-scaled", "vly-ag02-popavg") #c("vsl-epa-scaled", "vsl-epa-popavg", "vsl-ag02-scaled", "vsl-ag02-popavg")
initial.temperature <- NA # If NA, rebase temperature
temperature.description <- "Temperature change since 1980"
impact.description <- "Population Average VSL-monetized deaths (% GDP)"
include.climadapt <- F
include.intercept <- F

for (ii in 1:length(impcols)) {
    print(impcols[ii])
    for (jj in 1:3) {
        costs <- c("wo_costs", "costs_ub", "costs_lb")[jj]
        costprefix <- c("woc", "cub", "clb")[jj]

        print(paste0(prefixs[ii], '-', costprefix))

        prefix <- paste0(prefixs[ii], '-', costprefix)
        impcol <- gsub("COSTS", costs, impcols[ii])
        estimate.scc(filetemplate, prefix, tascol, impcol, initial.temperature, temperature.description, impact.description, include.climadapt, include.intercept)
    }
}
