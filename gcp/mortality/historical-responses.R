setwd("~/research/gcp/mortality")

library(ggplot2)

do.clipping <- T
do.diffclip <- T
df <- read.csv("~/research/gcp/socioeconomics/rep_regions_kmeans/rep_regions_mortcovar.csv")

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

get.curvedf <- function(name, gammas, climtas, loggdppc) {
    TT <- seq(-20, 40, by=1)

    if (do.clipping) {
        yy0 <- get.curve(TT, gammas, climtas, loggdppc)
        ii.min <- which.min(yy0[TT >= 10 & TT <= 25]) + which(TT == 10) - 1

        yy <- pmax(yy0 - yy0[ii.min], 0)
        if (do.diffclip) {
            yy.nd <- yy
            yy[ii.min:length(yy)] <- cummax(yy[ii.min:length(yy)])
            yy[1:(ii.min-1)] <- rev(cummax(rev(yy[1:(ii.min-1)])))

            data.frame(name=rep(name, 2), TT=rep(TT, 2), yy=c(yy.nd, yy), diffclip=rep(c("Original", "Deriv. Clip"), each=length(yy)), clipped=c(yy.nd == 0 & TT != TT[ii.min], yy == 0 & TT != TT[ii.min]))
        } else
            data.frame(name, TT, yy, clipped=(yy == 0 & TT != TT[ii.min]))
    } else {
        yy1 <- get.curve(TT, gammas, climtas, loggdppc)
        yy <- yy1 - yy1[TT == 20]

        if (do.diffclip) {
            yy.nd <- yy
            yy[ii.min:length(yy)] <- cummax(yy[ii.min:length(yy)])
            yy[1:(ii.min-1)] <- rev(cummax(rev(yy[1:(ii.min-1)])))
            data.frame(name=rep(name, 2), TT=rep(TT, 2), yy=c(yy.nd, yy), diffclip=rep(c("Original", "Deriv. Clip"), each=length(yy)), clipped=c(yy.nd == 0 & TT != TT[ii.min], yy == 0 & TT != TT[ii.min]))
        } else
            data.frame(name, TT, yy, clipped=(yy == 0 & TT != TT[ii.min]))
    }
}

allcurves <- data.frame()
for (ii in 1:nrow(df)) {
    thiscurve <- get.curvedf(df$jco[ii], sapply(csvv[3,], function(x) as.numeric(as.character(x))), df$climtas[ii], df$loggdppc[ii])
    allcurves <- rbind(allcurves, thiscurve)
}

ggplot(subset(allcurves, diffclip == "Original"), aes(TT, yy)) +
    facet_wrap(~ name) +
    geom_line(aes(colour=clipped)) +
    geom_label(data=data.frame(name=df$jco), aes(x=10, y=50, label=name), cex=2) +
    theme_minimal() +
    ylab("Change in deaths / 100,000") +
    scale_x_continuous(expand=c(0, 0), breaks=c(-15, 0, 15, 30)) + xlab("Daily temperature (C)") +
    scale_linetype_discrete(name=NULL) +
    scale_colour_manual(breaks=c(F, T), values=c("#000000", "#A01010")) +
    theme(
        strip.background = element_blank(),
        strip.text.x = element_blank(),
        legend.position="none"
    )


ggplot(allcurves, aes(TT, yy)) +
    facet_wrap(~ name) +
    geom_line(aes(linetype=diffclip, colour=clipped)) +
    geom_label(data=data.frame(name=df$jco), aes(x=10, y=50, label=name), cex=2) +
    theme_minimal() +
    ylab("Change in deaths / 100,000") +
    scale_x_continuous(expand=c(0, 0), breaks=c(-15, 0, 15, 30)) + xlab("Daily temperature (C)") +
    scale_linetype_discrete(name=NULL) +
    scale_colour_manual(breaks=c(F, T), values=c("#000000", "#A01010")) +
    theme(
        strip.background = element_blank(),
        strip.text.x = element_blank(),
        legend.position="none"
    )

