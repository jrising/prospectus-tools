source("damagefunc-lib.R")

path <- "august/poly5" # Source for the data files

library(pracma)

results <- data.frame(rcp=c(), ssp=c(), discountrate=c(), monetization=c(), scc=c())

xxtemplates <- c("damages_deaths_costs_COSTBOUND_vsl_SOURCE_WEIGHTS", "damages_lifeyears_costs_COSTBOUND_vly_SOURCE_WEIGHTS")

costtemplates <- c(xxtemplates, gsub("COSTBOUND", "ub", xxtemplates), gsub("COSTBOUND", "lb", xxtemplates))
fulltemplates <- c(gsub("SOURCE_WEIGHTS", "ag02_scaled", costtemplates), gsub("SOURCE_WEIGHTS", "ag02_popavg", costtemplates), gsub("SOURCE_WEIGHTS", "epa_scaled", costtemplates), gsub("SOURCE_WEIGHTS", "epa_popavg", costtemplates))
for (damagecol.template in fulltemplates) {

yys <- c()
XXs <- matrix(NA, 0, 5) # T, T^2, D[avgT], D[avgT^2], gdppc

for (rcp in c('rcp45', 'rcp85')) {
    for (ssp in c('SSP4', 'SSP1')) {
        if (rcp == 'rcp85' && ssp == 'SSP1')
            next
        print(c(rcp, ssp))
        damages <- read.csv(paste0(path, "/global_damages_", rcp, "_", ssp, ".csv"))

        for (gcm in unique(damages$gcm)) {
            for (mod in unique(damages$mod)) {
                subdmg <- damages[damages$gcm == gcm & damages$mod == mod,]
                if (nrow(subdmg) == 0)
                    next
                baseline <- sum(subdmg$global_tas[1:30] * (30:1) / sum(1:30))
                temps <- c(rep(0, 30), subdmg$global_tas - baseline)
                temps2 <- temps ^ 2

                ## Drop the last value, so resulting predictor is 1 year delayed
                avgtemps <- movavg(temps[-length(temps)], 30, 'w')
                avgtemps2 <- movavg(temps2[-length(temps)], 30, 'w')

                loggdppc <- lgfuns[[paste(mod, ssp, sep='-')]](subdmg$year)

                XXs <- rbind(XXs, cbind(tail(temps, nrow(subdmg)),
                                        tail(temps2, nrow(subdmg)),
                                        tail(avgtemps, nrow(subdmg)),
                                        tail(avgtemps2, nrow(subdmg)), loggdppc))
                yys <- c(yys, (subdmg[, gsub("COSTBOUND", "lb", damagecol.template)] + subdmg[, gsub("COSTBOUND", "ub", damagecol.template)]) / 2)
            }
        }
    }
}

##plot(XXs[, 1], yys)

library(rstan)
rstan_options(auto_write = TRUE)
options(mc.cores = parallel::detectCores())

stan.model <- "
data {
    int<lower=0> I;
    vector[I] T;
    vector[I] T2;
    vector[I] DavgT;
    vector[I] DavgT2;
    vector[I] logGDPpc;
    vector[I] y;
}
parameters {
    real alpha;
    real beta1;
    real<lower=0, upper=.05> beta2; // strong assumption, but need for convergence
    real<lower=0, upper=1> adapt;
    real<lower=-3, upper=0> gamma; // assumptions: doubling -> 12.5% of impact
    real<lower=0> epsilon;
}
model {
    y ~ normal(alpha + (beta1 * (T - adapt * DavgT) + beta2 * (T2 - adapt * DavgT2)) .* exp(gamma * logGDPpc), epsilon);
}"

inc <- !is.na(yys)
stan.data <- list(I = sum(inc), T = XXs[inc, 1], T2 = XXs[inc, 2], DavgT = XXs[inc, 3], DavgT2 = XXs[inc, 4], logGDPpc = XXs[inc, 5] - min(XXs[, 5]), y = yys[inc])

fit <- stan(model_code=stan.model, data=stan.data, iter = 1000, chains = 10)

la <- extract(fit, permute=T)

objective <- function(params) {
    alpha <- params[1]
    beta1 <- params[2]
    beta2 <- params[3]
    adapt <- params[4]
    gamma <- params[5]

    if (adapt < 0)
        return(Inf)

    yypreds <- alpha + (beta1 * (XXs[, 1] - adapt * XXs[, 3]) + beta2 * (XXs[, 2] - adapt * XXs[, 4])) * exp(gamma * (XXs[, 5] - min(XXs[, 5])))
    sum((yys - yypreds)^2, na.rm=T)
}

params <- c(mean(la$alpha), mean(la$beta1), mean(la$beta2), mean(la$adapt), mean(la$gamma))

1 - objective(params) / objective(c(mean(yys, na.rm=T), rep(0, 4)))

library(ggplot2)

ggplot(data.frame(x=c(la$alpha, la$beta1, la$beta2, la$adapt, la$gamma, la$epsilon),
                  group=rep(c("alpha", "beta1", "beta2", "adapt", "gamma", "sigma"), each=length(la$alpha))),
       aes(x)) +
    facet_wrap( ~ group, scales="free") + geom_density() + xlab("") + ylab("Density") + theme_bw()
ggsave(paste0("graphs/", damagecol.template, "-params.pdf"), width=8, height=6)

beta1 <- params[2]
beta2 <- params[3]
adapt <- params[4]
gamma <- params[5]

temps <- seq(0, max(XXs[, 1]), length.out=100)
weather.baseline <- (beta1 * temps + beta2 * temps^2)
climate.baseline <- (beta1 * (1 - adapt) * temps + beta2 * (1 - adapt) * temps^2)
climate.2050 <- (beta1 * (1 - adapt) * temps + beta2 * (1 - adapt) * temps^2) * exp(gamma * (mean(XXs[, 5]) - min(XXs[, 5])))

library(ggplot2)

ggplot(data.frame(temp=rep(temps, 3), damage=c(weather.baseline, climate.baseline, climate.2050), group=rep(c('Weather baseline', 'Climate baseline', 'Climate under 2050 income'), each=length(temps))),
       aes(temp, damage, colour=group)) +
    geom_line() + geom_hline(yintercept=0) + scale_x_continuous(expand=c(0, 0)) +
    theme_bw() + scale_colour_discrete(name="") + xlab("Temperature change from 1980") +
    ylab("Population Average VSL-montetized deaths (% GDP)") +
    theme(legend.position=c(.01, .99), legend.justification=c(0, 1)) +
    scale_y_continuous(labels = scales::percent)
ggsave(paste0("graphs/", damagecol.template, "-dmgfunc.pdf"), width=6, height=4)

## Calculate SCC
discountrate <- .03

social.costs <- function(temps, avgtemps, lgfun) {
    costs <- c()
    for (tt in 2017:2316) {
        temp <- temps[tt - 1980] - baseline
        avgtemp <- avgtemps[tt - 1980] - baseline
        loggdppc <- lgfun(tt)
        costs <- c(costs, mean((la$beta1 * (temp - la$adapt * avgtemp) + la$beta2 * (temp^2 - la$adapt * avgtemp^2)) * exp(la$gamma * (loggdppc - min(XXs[, 5])))))
    }

    costs
}

tempboost <- function(len) {
    (1 - exp(-(0:(len-1)) / 2.8)) * exp(-(0:(len-1)) / 400) * 9.3222e-13 / 0.96875 # Based on graphs.R
}

for (rcp in c('rcp45', 'rcp85')) {
    for (ssp in c('SSP4', 'SSP1')) {
        if (rcp == 'rcp85' && ssp == 'SSP1')
            next

        print(c(rcp, ssp))
        damages <- read.csv(paste0(path, "/global_damages_", rcp, "_", ssp, ".csv"))

        temps <- c()
        for (year in 1981:2099)
            temps <- c(temps, mean(damages$global_tas[damages$year == year]))
        baseline <- sum(temps[1:30] * (30:1) / sum(1:30))

        temps <- c(temps, rep(temps[length(temps)] - baseline, 300) * exp(-(0:299) / 400) + baseline)
        avgtemps <- movavg(temps, 30, 'w')

        costs1 <- social.costs(temps, avgtemps, lgfuns[[ssp]])
        costs2 <- social.costs(temps + tempboost(length(temps)), avgtemps + movavg(tempboost(length(temps)), 30, 'w'), lgfuns[[ssp]])

        for (discountrate in seq(0, .07, by=.01)) {
            scc <- sum((costs2 - costs1) * exp(-(0:299) * discountrate)) * 75.59e12
            results <- rbind(results, data.frame(rcp, ssp, discountrate, monetization=damagecol.template, scc))
        }
    }
}

save(la, file=paste0(damagecol.template, '-fit.RData'))
write.csv(results, "damagefunc-scc.csv", row.names=F)

}

library(reshape2)
library(xtable)

print(xtable(dcast(results, rcp + ssp + monetization ~ discountrate)), include.rownames=F)
