setwd("~/research/gcp/mortality")

library(ggplot2)

df <- read.csv("tas-dists.csv")
row0 <- 13

temps <- seq(-22.5, 42.5, by=1)

regdf <- data.frame(group=rep(c('Historical', 'RCP 8.5 2095'), each=length(temps)),
                    temps=rep(temps, 2),
                    counts=c(t(df[row0, -(1:2)]) / sum(t(df[row0, -(1:2)])),
                             t(df[row0+1, -(1:2)]) / sum(t(df[row0+1, -(1:2)]))))
regdf$group <- factor(regdf$group, c('RCP 8.5 2095', 'Historical'))
ggplot(regdf, aes(temps, counts, fill=group)) +
    geom_bar(stat="identity", position="dodge") + theme_minimal() +
    scale_x_continuous(expand=c(0, 0)) + ylab("Portion of days") +
    xlab("Daily temperature (C)") +
    scale_fill_discrete(name=NULL) +
    theme(legend.justification=c(1,1), legend.position=c(1,1))

