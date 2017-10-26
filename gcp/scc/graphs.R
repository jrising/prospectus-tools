library(ggplot2)

conc2ton <- 7.81e9 # 1 ppm = 2.13 GT C = 7.81 GT CO2

time <- seq(0, 1000, length.out=1000)
ppmtime <- exp(-time / 400) / conc2ton

pdf("pulse2ppm.pdf", width=6, height=4)
ggplot(data.frame(time, ppmtime), aes(time, ppmtime)) +
    geom_line() + scale_x_continuous(limits=c(0, 1000), expand=c(0, 0)) +
    scale_y_continuous(limits=c(0, 1/conc2ton), expand=c(0, 0)) +
    ylab(expression(paste("Change in ", CO[2], " cencentration (ppm)"))) + xlab("Years from pulse") +
    theme_bw() + ggtitle(expression(paste("Response of atmospheric ", CO[2], " concentration to 1 MT ", CO[2], " pulse"))) + theme(plot.margin = unit(c(0,.5,0,0), "cm"))
dev.off()

co2concs <- read.csv("co2conc.csv")

damages <- read.csv("global_damages_rcp85_SSP4.csv")
damages$co2 <- NA

for (ii in 1:nrow(damages))
    damages$co2[ii] <- conc2ton * co2concs$rcp85[co2concs$years == damages$year[ii] - 1]

mod <- lm(globa_tas ~ co2, data=damages)
summary(mod)

time <- seq(0, 300, length.out=1000)
temptime <- (1 - exp(-time / 2.8)) * exp(-time / 400) * mod$coeff[2]

pdf("pulse2temp.pdf", width=6, height=4)
ggplot(data.frame(time, temptime), aes(time, temptime)) +
    geom_line() + scale_x_continuous(limits=c(0, 300), expand=c(0, 0)) +
    scale_y_continuous(limits=c(0, mod$coeff[2]), expand=c(0, 0)) +
    ylab(expression(paste("Change in global temperature (C)"))) + xlab("Years from pulse") +
    theme_bw() + ggtitle(expression(paste("Response of global temperature to 1 MT ", CO[2], " pulse"))) + theme(plot.margin = unit(c(0,.5,0,0), "cm"))
dev.off()

