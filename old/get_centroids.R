setwd("~/groups/aggregator/trunk/tools")

library(PBSmapping)
counties <- importShapefile("../extras/UScounties/UScounties", readDBF=T)
cents <- calcCentroid(counties, rollup=1)
names <- attributes(counties)$PolyData$FIPS
write.table(cbind(as.character(names), cents$X, cents$Y), "../Aggregator/aggregator/public/data/centroids.csv", sep=",", quote=F, row.names=F, col.names=F)
