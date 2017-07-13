setwd("~/research/gcp/prospectus-tools/gcp/scc")

conc2ton <- 7.81e9 # 1 ppm = 2.13 GT C = 7.81 GT CO2
co2concs <- read.csv("co2conc.csv")

## Physical response
tt <- 0:(nrow(co2concs)-1)
physical <- (1 - exp(-tt / 2.8)) * exp(-tt / 400)

responses <- list()
responses[['physical']] <- physical

tau <- 77
for (kk in 0:2)
    responses[[paste0("t", kk, "exp")]] <- tt^kk * exp(-tt / tau)

included <- paste0('t', 0, 'exp') #c('physical', paste0("t", 0:2, "exp"))
T.powers <- 1

main <- "Damages under life years lost" #"Damages under Pop. Avg. VSL" #
damagecol1 <- 'damages_lifeyears_costs_lb_vly_scaled' #'damages_deaths_costs_lb_vsl_ag02_popavg' #
damagecol2 <- 'damages_lifeyears_costs_ub_vly_scaled' #'damages_deaths_costs_ub_vsl_ag02_popavg' #

yys <- c()
XXs <- matrix(NA, 0, length(included) * (T.powers + 1) + 1)

for (rcp in c('rcp45', 'rcp85')) {
    for (ssp in c('SSP4', 'SSP5')) {
        print(c(rcp, ssp))
        damages <- read.csv(paste0("global_damages_", rcp, "_", ssp, ".csv"))
        emits <- c(diff(co2concs[, rcp] * conc2ton), 0)

        for (gcm in unique(damages$gcm)) {
            subdmg <- damages[damages$gcm == gcm,]
            baseline <- sum(subdmg$globa_tas[1:30] * (30:1) / sum(1:30))
            temps <- c(rep(0, sum(co2concs$years < 1981)), subdmg$globa_tas - baseline)

            for (ii in 1:nrow(subdmg)) {
                ss <- subdmg$year[ii] - co2concs$year
                incl <- ss >= 0

                xx <- c(subdmg$gdp[ii])

                for (T.power in 0:T.powers) {
                    for (name in included) {
                        xi <- sum(emits[incl] * responses[[name]][ss[incl]+1] * temps[incl]^T.power) # temperature when emitted
                        xx <- c(xx, xi)
                    }
                }

                XXs <- rbind(XXs, xx)
            }

            yys <- c(yys, (subdmg[, damagecol1] + subdmg[, damagecol2]) / 2)
        }
    }
}

XXs <- cbind(1, XXs)

allnames <- c("const", "gdp")
for (T.power in 0:T.powers)
    allnames <- c(allnames, paste0(included, "T", T.power))

colnames(XXs) <- allnames

mod <- lm(yys ~ 0 + XXs)#[, c(1, 3, 7, 11)])
summary(mod)

## library(MASS)
## dfxx <- data.frame(XXs)
## ##fit <- lm(yys ~ gdp + physicalT0 + t0expT0 + t1expT0 + t2expT0 + physicalT1 + t0expT1 + t1expT1 + t2expT1 + physicalT2 + t0expT2 + t1expT2 + t2expT2, data=dfxx)
## fit <- lm(yys ~ gdp + t0expT0 + t0expT1 + t0expT2, data=dfxx)
## step <- stepAIC(fit, direction="both")#, k=log(nrow(XXs))) # Same result

tt <- 0:300

hh0 <- tt * 0
for (nn in 1:length(included))
    hh0 <- hh0 + mod$coeff[nn+1] * responses[[included[nn]]][tt + 1]

hh1 <- tt * 0
for (T.power in 0:T.powers) {
    for (nn in 1:length(included))
        hh1 <- hh1 + mod$coeff[T.power * length(included) + nn + 2] * responses[[included[nn]]][tt + 1] * 1^T.power
}

hh2 <- tt * 0
for (T.power in 0:T.powers) {
    for (nn in 1:length(included))
        hh2 <- hh2 + mod$coeff[T.power * length(included) + nn + 2] * responses[[included[nn]]][tt + 1] * 2^T.power
}

hh4 <- tt * 0
for (T.power in 0:T.powers) {
    for (nn in 1:length(included))
        hh4 <- hh4 + mod$coeff[T.power * length(included) + nn + 2] * responses[[included[nn]]][tt + 1] * 4^T.power
}

library(ggplot2)

ggplot(data.frame(year=c(tt, tt), damage=c(hh0, hh1, hh2, hh4) * 75.59e12, context=rep(c("Baseline", "+ 1 C", "+ 2 C", "+ 4 C"), each=length(tt))),
       aes(year, damage, colour=context)) +
    geom_line() + theme_bw() + xlab("Year from emission") + ylab(main) +
    scale_colour_discrete(name="")

discountrate <- .03

sum(hh0 * exp(-tt * discountrate)) * 75.59e12 # VSL: 0; LYL: 0
sum(hh1 * exp(-tt * discountrate)) * 75.59e12 # VSL: 11.14; LYL: 1.42
sum(hh2 * exp(-tt * discountrate)) * 75.59e12 # VSL: 21.41; LYL: 4.54
sum(hh4 * exp(-tt * discountrate)) * 75.59e12 # VSL: 41.95; LYL: 10.79

## In time
for (rcp in c('rcp45', 'rcp85')) {
    for (ssp in c('SSP4', 'SSP5')) {
        print(c(rcp, ssp))
        damages <- read.csv(paste0("global_damages_", rcp, "_", ssp, ".csv"))

        temps <- c()
        for (year in 1981:2099)
            temps <- c(temps, mean(damages$globa_tas[damages$year == year]))
        temps <- c(temps, rep(temps[length(temps)], 300))

        baseline <- sum(temps[1:30] * (30:1) / sum(1:30))

        hh2017 <- tt * 0
        for (T.power in 0:T.powers) {
            for (nn in 1:length(included))
                hh2017 <- hh2017 + mod$coeff[T.power * length(included) + nn + 2] * responses[[included[nn]]][tt + 1] * (temps[tt + which((1981:2099) == 2017)] - baseline)^T.power
        }

        print(sum(hh2017 * exp(-tt * discountrate)) * 75.59e12)
    }
}

## VSL: 10.63 - 12.90 (RCP 4.5); 15.16 - 17.57 (RCP 8.5)
## LYL: 1.27 - 1.96 (RCP 4.5); 2.64 - 3.38 (RCP 8.5)
