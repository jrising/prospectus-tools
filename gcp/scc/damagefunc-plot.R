setwd("~/research/gcp/prospectus-tools/gcp/scc")

source("damagefunc-lib.R")

library(ggplot2)

allloggdppc <- c()
alltemps <- c()
for (rcp in c('rcp45', 'rcp85')) {
    for (ssp in c('SSP4', 'SSP5')) {
        if (rcp == 'rcp85' && ssp == 'SSP5')
            next # XXX: Nonexistant combination
        print(c(rcp, ssp))
        damages <- read.csv(paste0("global_damages_", rcp, "_", ssp, ".csv"))
        for (gcm in unique(damages$gcm)) {
            for (mod in unique(damages$mod)) {
                subdmg <- damages[damages$gcm == gcm & damages$mod == mod,]
                if (nrow(subdmg) == 0)
                    next

                baseline <- sum(subdmg$global_tas[1:30] * (30:1) / sum(1:30))
                temps <- c(rep(0, 30), subdmg$global_tas - baseline)

                loggdppc <- lgfuns[[paste(mod, ssp, sep='-')]](subdmg$year)
                allloggdppc <- c(allloggdppc, loggdppc)
                alltemps <- c(alltemps, temps)
            }
        }
    }
}

for (damagecol.template in c("damages_deaths_costs_XX_vsl_ag02_popavg", "damages_lifeyears_costs_XX_vly_popavg", "damages_lifeyears_costs_XX_vly_scaled", "damages_deaths_costs_XX_vsl_ag02_scaled")) {
    load(paste0(damagecol.template, '-fit.RData'))

    temps <- seq(0, max(temps), length.out=100)
    df <- data.frame(temp=c(), group=c(), y=c(), ymin=c(), ymax=c())

    for (temp in temps) {
        weather.base <- (la$beta1 * temp + la$beta2 * temp^2)
        climate.base <- (la$beta1 * (1 - la$adapt) * temp + la$beta2 * (1 - la$adapt) * temp^2)
        climate.2050 <- (la$beta1 * (1 - la$adapt) * temp + la$beta2 * (1 - la$adapt) * temp^2) * exp(la$gamma * (mean(allloggdppc) - min(allloggdppc)))

        df <- rbind(df, data.frame(temp, group=c("weather.base", "climate.base", "climate.2050"),
                                   y=c(mean(weather.base), mean(climate.base), mean(climate.2050)),
                                   ymin=c(quantile(weather.base, probs=.025), quantile(climate.base, probs=.025), quantile(climate.2050, probs=.025)),
                                   ymax=c(quantile(weather.base, probs=.975), quantile(climate.base, probs=.975), quantile(climate.2050, probs=.975))))
    }

    pdf(paste0("graphs/", damagecol.template, "-damagefunc2.pdf"), width=6, height=4)
    ggplot(df, aes(temp, group=group)) +
        geom_line(aes(y=y, colour=group), size=1) +
        geom_ribbon(aes(ymin=ymin, ymax=ymax, fill=group, alpha=group)) +
        scale_colour_discrete(name="",
                              breaks=c("weather.base", "climate.base", "climate.2050"),
                              labels=c('Weather baseline', 'Climate baseline', 'Climate under 2050 income')) +
        scale_fill_discrete(name="", breaks=c("weather.base", "climate.base", "climate.2050"),
                            labels=c('Weather baseline', 'Climate baseline', 'Climate under 2050 income')) +
        scale_alpha_manual(name="", labels=c('Weather baseline', 'Climate baseline', 'Climate under 2050 income'),
                           breaks=c("weather.base", "climate.base", "climate.2050"),
                           values=c(.5, 0, .5)) +
        geom_hline(yintercept=0) + scale_x_continuous(expand=c(0, 0)) +
        theme_bw() + xlab("Temperature change from 1980") +
        ylab("Population Average VSL-montetized deaths (% GDP)") +
        theme(legend.position=c(.01, .99), legend.justification=c(0, 1)) +
        scale_y_continuous(labels = scales::percent)
    dev.off()
}

library(pracma)

tempboost <- function(len) {
    (1 - exp(-(0:(len-1)) / 2.8)) * exp(-(0:(len-1)) / 400) * 9.3222e-13 / 0.96875 # Based on graphs.R
}

loggdppcs <- lgfuns[["SSP4"]](2017:(2017+299))

df <- data.frame(temp0=c(), tt=c(), y=c(), ymin=c(), ymax=c())

for (temp0 in c(0, 1, 2, 4)) {
    temp1 <- temp0 + tempboost(300)
    avgtemp1 <- movavg(temp1, 30, 'w')

    for (tt in 0:299) {
        histclim <- (la$beta1 * (1 - la$adapt) * temp0 + la$beta2 * (1 - la$adapt) * temp0^2) * exp(la$gamma * (loggdppcs[tt+1] - min(allloggdppc)))
        response <- (la$beta1 * (temp1[tt+1] - la$adapt * avgtemp1[tt+1]) + la$beta2 * (temp1[tt+1]^2 - la$adapt * avgtemp1[tt+1]^2)) * exp(la$gamma * (loggdppcs[tt+1] - min(allloggdppc)))

        df <- rbind(df, data.frame(temp0, tt, y=mean(response - histclim), ymin=quantile(response - histclim, probs=.025, na.rm=T), ymax=quantile(response - histclim, probs=.975, na.rm=T)))
    }
}

pdf("graphs/pulse2cost.pdf", width=6, height=4)
ggplot(df, aes(tt, y * 75.59e12)) +
    geom_line(aes(colour=as.factor(temp0))) + geom_ribbon(aes(ymin=ymin * 75.59e12, ymax=ymax * 75.59e12, fill=as.factor(temp0)), alpha=.5) +
    scale_x_continuous(limits=c(0, 300), expand=c(0, 0)) +
    scale_fill_discrete(name="", labels=c("Baseline", "+ 1 C", "+ 2 C", "+ 4 C")) +
    scale_colour_discrete(name="", labels=c("Baseline", "+ 1 C", "+ 2 C", "+ 4 C")) +
    ylab(expression(paste("Loss to society (current USD)"))) + xlab("Years from pulse") +
    theme_bw() + ggtitle(expression(paste("Response of social damages to 1 MT ", CO[2], " pulse"))) + theme(plot.margin = unit(c(0,.5,0,0), "cm")) +
    theme(legend.position = c(.99, .99), legend.justification=c(1, 1))
dev.off()

sum(subset(df, temp0 == 1)$y * exp(-.03 * (0:299))) * 75.59e12
