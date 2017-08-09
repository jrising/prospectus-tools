setwd("~/research/gcp/prospectus-tools/gcp/scc")

library(reshape2)
library(dplyr)

## Calculate global GDPpc
gdppc <- read.csv("gdp_per_capita.csv")
poptot <- read.csv("total_population.csv")

gdppc2 <- melt(gdppc, id.vars=c('MODEL', 'SCENARIO', 'REGION'))
gdppc2$year <- as.numeric(substr(gdppc2$variable, 2, 5))
gdppc2$gdppc <- gdppc2$value
poptot2 <- melt(poptot[, c(1:3, 9:ncol(poptot))], id.vars=c('MODEL', 'SCENARIO', 'REGION'))
poptot2$year <- as.numeric(substr(poptot2$variable, 2, 5))
poptot2$poptot <- poptot2$value

combo <- gdppc2 %>% left_join(poptot2, c("MODEL", "SCENARIO", "REGION", "year"))
combo$ssp <- substr(combo$SCENARIO, 1, 4)

allgdppcs <- data.frame(model=c(), ssp=c(), year=c(), gdppc=c())

for (model in unique(combo$MODEL)) {
    for (scenario in unique(combo$ssp)) {
        for (yr in unique(combo$year)) {
            modcombo <- subset(combo, MODEL == model & ssp == scenario & year == yr)
            values <- modcombo$gdppc * modcombo$poptot
            avg <- sum(values, na.rm=T) / sum(modcombo$poptot[!is.na(values)])

            allgdppcs <- rbind(allgdppcs, data.frame(model, ssp=scenario, year=yr, gdppc=avg))
        }
    }
}


allgdppcs$model <- as.character(allgdppcs$model)
allgdppcs$model[allgdppcs$model == "OECD Env-Growth"] <- "high"
allgdppcs$model[allgdppcs$model == "IIASA GDP"] <- "low"

lgfuns <- list() # 'model-ssp' = function
for (model in c('low', 'high'))
    for (ssp in c('SSP4', 'SSP5')) {
        subag <- allgdppcs[allgdppcs$model == model & allgdppcs$ssp == ssp,]
        fn <- splinefun(subag$year, log(subag$gdppc), method="natural")
        lgfuns[[paste(model, ssp, sep='-')]] <- fn
    }

lgfuns[["SSP4"]] <- function(x) (lgfuns[["low-SSP4"]](x) + lgfuns[["high-SSP4"]](x)) / 2
lgfuns[["SSP5"]] <- function(x) (lgfuns[["low-SSP5"]](x) + lgfuns[["high-SSP5"]](x)) / 2
