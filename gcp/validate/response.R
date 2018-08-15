setwd("~/research/gcp/mortality")

library(ggplot2)
library(mvtnorm)

do.clipping <- T
region = 'USA.27.1625'

if (region == 'india') {
    climtas0 <- 25.743467442791619
    loggdppc0 <- 8.0072716568734776
    climtas1 <- 29.533672020543936
    loggdppc1 <- 9.5337815088315914
} else if (region == 'chicago') {
    climtas0 <- 10.69911999868895
    loggdppc0 <- 10.976412876992653
    climtas1 <- 14.856286905048741
    loggdppc1 <- 11.601797621813535
} else if (region == 'USA.10.367') {
    climtas0 <- 24.98685267495889
    loggdppc0 <- 10.71664352189571
    climtas1 <- 27.381088673907037
    loggdppc1 <- 11.331317614833411
} else if (region == 'ETH.8.39.Rce1a51acb321322b') {
    climtas0 <- 17.024671350250433
    loggdppc0 <- 6.8203388118575372
    climtas1 <- 20.24106996072404
    loggdppc1 <- 8.929062644792884
} else if (region == 'AUS.11.1392') {
    climtas0 <- 28.870636687834644
    loggdppc0 <- 10.415717033929447
    climtas1 <- 31.758403234849148
    loggdppc1 <- 11.073917923800922
} else if (region == 'AGO.11.94') {
    climtas0 <- 25.30318678946287
    loggdppc0 <- 8.9125183548779905
    climtas1 <- 27.853115628738252
    loggdppc1 <- 9.5003513061209262
} else if (region == 'OMN.8') {
    climtas0 <- 27.056305161390981
    loggdppc0 <- 10.268814628039628
    climtas1 <- 30.311526744901556
    loggdppc1 <- 10.839057671756249
} else if (region == 'ARE.1') {
    climtas0 <- 27.770774678467525
    loggdppc0 <- 10.510277794127644
    climtas1 <- 31.333509459811335
    loggdppc1 <- 10.921264957500616
} else if (region == 'USA.27.1625') {
    climtas0 <- 8.1895056132779356
    loggdppc0 <- 10.586498743182688
    climtas1 <- 12.242089761375349
    loggdppc1 <- 11.201172836120389
}

csvv <- read.csv("Agespec_interaction_GMFD_POLY-4_TINV_CYA_NW_w1.csv", header=F)
csvv <- csvv[, 25:36]

get.gamma <- function(gammas, pred, covar) gammas[csvv[1,] == pred & csvv[2,] == covar]

get.curve <- function(TT, gammas, climtas, loggdppc) {
    beta1 <- get.gamma(gammas, 'tas', '1') + get.gamma(gammas, 'tas', 'climtas') * climtas + get.gamma(gammas, 'tas', 'loggdppc') * loggdppc
    beta2 <- get.gamma(gammas, 'tas2', '1') + get.gamma(gammas, 'tas2', 'climtas') * climtas + get.gamma(gammas, 'tas2', 'loggdppc') * loggdppc
    beta3 <- get.gamma(gammas, 'tas3', '1') + get.gamma(gammas, 'tas3', 'climtas') * climtas + get.gamma(gammas, 'tas3', 'loggdppc') * loggdppc
    beta4 <- get.gamma(gammas, 'tas4', '1') + get.gamma(gammas, 'tas4', 'climtas') * climtas + get.gamma(gammas, 'tas4', 'loggdppc') * loggdppc

    beta1 * TT + beta2 * TT^2 + beta3 * TT^3 + beta4 * TT^4
}

get.curvedf <- function(name, gammas, histall=F, histtemp=F) {
    TT <- seq(-23, 41, by=1)

    if (do.clipping) {
        yy0 <- get.curve(TT, gammas, climtas0, loggdppc0)
        ii.min <- which.min(yy0[TT >= 10 & TT <= 25]) + which(TT == 10) - 1

        if (histall)
            return(data.frame(name, TT, yy=pmax(yy0 - yy0[ii.min], 0)))

        if (histtemp)
            yy1 <- get.curve(TT, gammas, climtas0, loggdppc1)
        else
            yy1 <- get.curve(TT, gammas, climtas1, loggdppc1)
        yy1 <- yy1 - yy1[ii.min]

        if (histtemp)
            yyg <- get.curve(TT, gammas, climtas0, loggdppc0)
        else
            yyg <- get.curve(TT, gammas, climtas1, loggdppc0)
        yyg <- yyg - yyg[ii.min]

        data.frame(name, TT, yy=pmax(pmin(yy1, yyg), 0)) # Good money and clipping
    } else {
        if (histtemp)
            yy1 <- get.curve(TT, gammas, climtas0, loggdppc1)
        else
            yy1 <- get.curve(TT, gammas, climtas1, loggdppc1)
        data.frame(name, TT, yy=yy1 - yy1[TT == 20])
    }
}

meddf <- get.curvedf('RCP 8.5 2095', sapply(csvv[3,], function(x) as.numeric(as.character(x))))
meddf0 <- get.curvedf('Counterfactual', sapply(csvv[3,], function(x) as.numeric(as.character(x))), histtemp=T)
meddf00 <- get.curvedf('Historical', sapply(csvv[3,], function(x) as.numeric(as.character(x))), histall=T)

ggplot(rbind(meddf, meddf0, meddf00), aes(TT, yy, colour=name, linetype=name)) +
    geom_line() + theme_minimal() +
    ylab("Change in deaths / 100,000") +
    scale_x_continuous(expand=c(0, 0)) + xlab("Daily temperature (C)") +
    scale_colour_discrete(name=NULL) +
    scale_linetype_discrete(name=NULL) +
    theme(legend.justification=c(1,1), legend.position=c(1,1))
