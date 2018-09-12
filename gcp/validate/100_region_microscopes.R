rm(list = ls())

library(ggplot2)
library(mvtnorm)
library(magrittr)
library(dplyr)
library(stringr)
library(plyr)

#------------------------------------------------------------------------------------------

model <- "poly" #poly or spline
agelist <- list("young","older","oldest")
#age <- "oldest"
do.clipping <- T 

#for poly model only
do.diffclip <- F

#for spline model only
low <- 20 #low kink
high <- 25 #high kink
order.low <- 1 #order of low kink
order.high <- 3 #order of high kink

#set directory
wd <- "sacagawea" #"local" or "sacagawea"
dir <- ifelse(wd == "local", "/Users/trinettachong/Dropbox", "/local/shsiang/Dropbox")
csvv.dir <- paste0(dir,"/Global ACP/ClimateLaborGlobalPaper/Paper/Datasets/Trin_test/Mortality/timeseries/") 
csvv.name <- ifelse(model == "poly", "Agespec_interaction_GMFD_POLY-4_TINV_CYA_NW_w1.csvv", paste0("Agespec_interaction_response_polyspline_",low,"C_",high,"C_order2_GMFD.csvv"))
outputwd <- ifelse(wd == "local", paste0(csvv.dir, "response/"), paste0(dir,"/Global ACP/MORTALITY/Replication_2018/3_Output/6_projection/regionmicroscopes/100_regions/"))

#------------------------------------------------------------------------------------------

for (age in agelist){
  
#read csvv
skip.no <- ifelse(model == "poly", 18,  16) #lines to skip when loading csvv, 18 for poly4, 16 for hddcdd 
csvv <- read.csv(paste0(csvv.dir, csvv.name), skip = skip.no, header = F, sep= ",", stringsAsFactors = T)

squish_function <- stringr::str_squish #I have to do this because annoying str_squish function doesn't work on sacagawea

#subset to relevant rows & remove blank spaces in characters
csvv <- csvv[-c(2,4,6, nrow(csvv)-1, nrow(csvv)), ] %>%
  rowwise() %>%
  mutate_all(funs(squish_function(.))) %>%
  ungroup()

#extract only cols from specified age group
col.interval <- ifelse(model == "poly", 11, 5) #length of gamma values in csvv minus 1, 11 for poly4, 5 for hddcdd
if (age=="oldest"){
  csvv <- csvv[, (3+2*col.interval):(3+3*col.interval)] 
} else if (age == "young"){
  csvv <- csvv[, 1:(1+col.interval)] 
} else {
  csvv <- csvv[, (2+col.interval):(2+2*col.interval)] 
}

#load covariates
df <- read.csv(paste0(dir, "/Global ACP/ClimateLaborGlobalPaper/Paper/Datasets/Trin_test/Trin_test/socioeconomics/rep_regions_kmeans/rep_regions_mortcovar_trin.csv"))

#create master df
master <- data.frame()

#plot.response <- function(region){

for (region in as.list(levels(df$jco))){
  
  #assign covariates
  climtas0 <- df$climtas0[df$jco == region] 
  loggdppc0 <- df$loggdppc0[df$jco == region] 
  climtas1 <- df$climtas1[df$jco == region] 
  loggdppc1 <- df$loggdppc1[df$jco == region] 
  
  get.gamma <- function(gammas, pred, covar) gammas[csvv[1,] == pred & csvv[2,] == covar]
  
  get.curve <- function(TT, gammas, climtas, loggdppc) { 
    
    if (model == "poly"){
      
      beta1 <- get.gamma(gammas, 'tas', '1') + get.gamma(gammas, 'tas', 'climtas') * climtas + get.gamma(gammas, 'tas', 'loggdppc') * loggdppc
      beta2 <- get.gamma(gammas, 'tas2', '1') + get.gamma(gammas, 'tas2', 'climtas') * climtas + get.gamma(gammas, 'tas2', 'loggdppc') * loggdppc
      beta3 <- get.gamma(gammas, 'tas3', '1') + get.gamma(gammas, 'tas3', 'climtas') * climtas + get.gamma(gammas, 'tas3', 'loggdppc') * loggdppc
      beta4 <- get.gamma(gammas, 'tas4', '1') + get.gamma(gammas, 'tas4', 'climtas') * climtas + get.gamma(gammas, 'tas4', 'loggdppc') * loggdppc
      
      beta1 * TT + beta2 * TT^2 + beta3 * TT^3 + beta4 * TT^4
      
    } else { #spline
      
      yy0_low <- (get.gamma(gammas, paste0('hdd',low),'1') + get.gamma(gammas, paste0('hdd',low),'climtas')*climtas + get.gamma(gammas, paste0('hdd',low),'loggdppc')*loggdppc)*TT[1:(24 + low)]
      yy0_high <- (get.gamma(gammas, paste0('cdd',high),'1') + get.gamma(gammas,  paste0('cdd',high),'climtas')*climtas + get.gamma(gammas, paste0('cdd',high),'loggdppc')*loggdppc)*TT[(24 + high):length(TT)]
      yy0_mid <- 0*TT[(25+low):(24+high-1)]
      
      c(yy0_low, yy0_mid, yy0_high) #concatenate all 3 chunks 
      
    }
  }
  
  get.curvedf <- function(name, gammas, histall=F, histtemp=F) {
    
    if (model == "poly") {
      
      TT <- seq(-23, 41)
      
      if (do.clipping) {
        
        yy0 <- get.curve(TT, gammas, climtas0, loggdppc0) 
        ii.min <- which.min(yy0[TT >= 10 & TT <= 25]) + which(TT == 10) - 1 
        
        yy <- pmax(yy0 - yy0[ii.min], 0) #goodmoney clipping
        
        if (do.diffclip) { #u-clipping
          yy.nd <- yy
          yy[ii.min:length(yy)] <- cummax(yy[ii.min:length(yy)]) #returns a vector with the cum max value ('max value to date')
          yy[1:(ii.min-1)] <- rev(cummax(rev(yy[1:(ii.min-1)])))
          } 

        if (histall) #Historical (response at t0)
          return(data.frame(name, TT, yy)) #meddf00
        
        if (histtemp) #Counterfactual (histclim)
          yy1 <- get.curve(TT, gammas, climtas0, loggdppc1) # Counterfactual response (i.e. response at t1, where there's no climate change, but allow income to adapt)
        else
          yy1 <- get.curve(TT, gammas, climtas1, loggdppc1) # Response at t1, where there is climate change, and allow income to adapt  
          yy1 <- yy1 - yy1[ii.min] 
        
        if (histtemp)
          yyg <- get.curve(TT, gammas, climtas0, loggdppc0) # calculate response at t0 
        else
          yyg <- get.curve(TT, gammas, climtas1, loggdppc0) # calculate response at t1, no income adapt, only climate adapt
          yyg <- yyg - yyg[ii.min]
        
        yy <- (pmax(pmin(yy1, yyg), 0)) #Good money and clipping 
        
        if (do.diffclip) { #u-clipping
          yy.nd <- yy
          yy[ii.min:length(yy)] <- cummax(yy[ii.min:length(yy)]) #returns a vector with the cum max value ('max value to date')
          yy[1:(ii.min-1)] <- rev(cummax(rev(yy[1:(ii.min-1)])))
        } 
        
        data.frame(name, TT, yy) #Good money and clipping 
        
        
      } else { #no good money nor clipping
        
        if (histtemp)
          yy1 <- get.curve(TT, gammas, climtas0, loggdppc1) #calculate histclim
        else
          yy1 <- get.curve(TT, gammas, climtas1, loggdppc1) #calculate response at t1, where there is climate change, and income adaptation
        
        if (do.diffclip) { #u-clipping
          yy <- yy1
          yy[ii.min:length(yy)] <- cummax(yy[ii.min:length(yy)]) #returns a vector with the cum max value ('max value to date')
          yy[1:(ii.min-1)] <- rev(cummax(rev(yy[1:(ii.min-1)])))
        } 
        
        data.frame(name, TT, yy) 
        
      }
      
    } else { #spline
      
      TT <- seq(-23, 41) #create vector of temperatures
      TT[1:(24 + low)] <- (low - TT[1:(24 + low)])^order.low #recode temperatures for below the low kink
      TT[(24 + high):length(TT)] <- (TT[(24 + high):length(TT)] - high)^order.high #recode temperatures for above the high kink
      TT[(25+low):(24+high-1)] <- 0 #recode temperatures between kinks to be zero
      
      if (do.clipping) {
        yy0 <- get.curve(TT, gammas, climtas0, loggdppc0) # calculate response at t0
        
        if (histall) #Historical (response at t0)
          return(data.frame(name, TT, yy=pmax(yy0, 0))) #meddf00
        
        if (histtemp) #Counterfactual (histclim)
          yy1 <- get.curve(TT, gammas, climtas0, loggdppc1) # Counterfactual response (i.e. response at t1, where there's no climate change, but allow income to adapt)
        else
          yy1 <- get.curve(TT, gammas, climtas1, loggdppc1) # calculate response at t1, where there is climate change, and allow income to adapt  
        
        if (histtemp)
          yyg <- get.curve(TT, gammas, climtas0, loggdppc0) #calculate response at t0 
        else
          yyg <- get.curve(TT, gammas, climtas1, loggdppc0) #calculate response at t1, no income adapt, only climate adapt
        
        data.frame(name, TT, yy=pmax(pmin(yy1, yyg), 0)) #Good money and clipping 
        
      } else { #no good money nor clipping
        
        if (histtemp)
          yy1 <- get.curve(TT, gammas, climtas0, loggdppc1) #calculate histclim
        else
          yy1 <- get.curve(TT, gammas, climtas1, loggdppc1) #calculate response at t1, where there is climate change, and income adaptation
        data.frame(name, TT, yy=yy1) 
      }
    }
    
  }
  
  meddf <- get.curvedf('RCP 8.5 2095', sapply(csvv[3,], function(x) as.numeric(as.character(x))))
  meddf$temp <- seq(-23, 41)
  meddf0 <- get.curvedf('Counterfactual', sapply(csvv[3,], function(x) as.numeric(as.character(x))), histtemp=T)
  meddf0$temp <- seq(-23, 41)
  meddf00 <- get.curvedf('Historical', sapply(csvv[3,], function(x) as.numeric(as.character(x))), histall=T)
  meddf00$temp <- seq(-23, 41)
  
  plotdf <- rbind(meddf, meddf0, meddf00) #combine all 3 scenarios
  plotdf$jco <- region #add name column
  
  #plot individual responses
  suffix <- ifelse(do.diffclip==T, "_u", "")
  plotname <- ifelse(model == "poly", paste0("response-", region,"_",age,"_poly",suffix,".pdf"), paste0("response-", region,"_",age,"_",low, "_", high,"_",order.low,"_",order.high,".pdf"))
  masterplotname <- ifelse(model == "poly", paste0("response-",age,"_poly",suffix,".pdf"), paste0("response-",age,"_",low, "_", high,"_",order.low,"_",order.high,".pdf"))
  
  print(paste0("plotting ", region))
  
  ggplot(plotdf, aes(x = temp, y = yy, colour=name, linetype=name)) +
    geom_line() + theme_minimal() +
    ylab("Change in deaths / 100,000") +
    scale_x_continuous(expand=c(0, 0)) + xlab("Daily temperature (C)") +
    scale_colour_discrete(name=NULL) +
    scale_linetype_discrete(name=NULL) +
    theme(legend.justification=c(1,1), legend.position=c(1,1))
  ggsave(paste0(outputwd, plotname), width=8, height=2.5)
  
  #get individual plots ready for 10 x 10 figure
  if (region == as.list(levels(df$jco))[1]) {
    master <- plotdf #if it is the first region in the list, assign to master
    } else {
    master <- rbind(master, plotdf) #if it is not the 1st region in the list, rowbind with master
  }
}

#plot 100 regions matrix
print(paste0("plotting 100 regions ", age))

if (age=="oldest"){
  labelyaxis <- 100
  } else if (age=="young") {
  labelyaxis <- 7.5
  } else {
  labelyaxis <- 1
  }


ggplot(master, aes(x = temp, y = yy)) +
  facet_wrap(~ jco) +
  geom_line(aes(colour=name, linetype=name), size = .5) +
  geom_label(aes(x=10, y=labelyaxis, label=master$jco), cex=2) +
  theme_minimal() +
  ylab("Change in deaths / 100,000") +
  scale_x_continuous(expand=c(0, 0), breaks=c(-15, 0, 15, 30)) + xlab("Daily temperature (C)") +
  scale_linetype_discrete(name=NULL) +
  #scale_colour_manual(breaks=c(F, T), values=c("#000000", "#A01010")) +
  theme(strip.background = element_blank(),
    strip.text.x = element_blank(),
    legend.position="none")
ggsave(paste0(outputwd, masterplotname), width = 10, height = 10)

}

#lapply(as.list(levels(df$jco)), plot.response)  #apply plot.response function to all 100 regions


