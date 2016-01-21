library(devtools)
library(roxygen2)

setwd("~/projects/dmas/tools/import/rdmas")
document()
setwd("..")
install("rdmas")

ctl <- c(4.17,5.58,5.18,6.11,4.50,4.61,5.17,4.53,5.33,5.14)
trt <- c(4.81,4.17,4.41,3.59,5.87,3.83,6.03,4.89,4.32,4.69)
group <- gl(2, 10, 20, labels = c("Ctl","Trt"))
weight <- c(ctl, trt)
lm.D9 <- lm(weight ~ group)

dmas.put.model(lm.D9, "4sW2Txtsn8o3bkwY", "LEAVE-BLANK")
dmas.extract.single("4sW2Txtsn8o3bkwY", "groupTrt", "LEAVE-BLANK")

library(lfe)

## create covariates
x <- rnorm(1000)
x2 <- rnorm(length(x))

## individual and firm
id <- factor(sample(20,length(x),replace=TRUE))
firm <- factor(sample(13,length(x),replace=TRUE))

## effects for them
id.eff <- rnorm(nlevels(id))
firm.eff <- rnorm(nlevels(firm))

## left hand side
u <- rnorm(length(x))
y <- x + 0.5*x2 + id.eff[id] + firm.eff[firm] + u

## estimate and print result
est <- felm(y ~ x+x2| id + firm)

dmas.put.model(est, "4sW2Txtsn8o3bkwY", "LEAVE-BLANK")

