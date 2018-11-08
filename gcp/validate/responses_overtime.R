#------------------------------------------------------------------------------------------
# IR responses overtime

# This script plots the response function(s) of impact region(s) over time.

# Sector: Mortality
# Updated 4 Oct 2018 by Trinetta Chong 

#------------------------------------------------------------------------------------------

rm(list = ls())

library(ggplot2)
library(mvtnorm)
library(magrittr)
library(dplyr)
library(stringr)
library(readstata13)
library(viridis)
library(gridExtra)
library(grid)
library(lattice)

#------------------------------------------------------------------------------------------
#set up parameters

model <- "poly" #poly or spline
agelist <- list("young","older","oldest")
yearlist <- seq(2010, 2099) #define time period to plot response functions
plot.histogram <- F #plot histogram below response?
regionlist <- list("USA.14.608", "USA.33.1833", "USA.3.103", "USA.3.102", "USA.3.101") #define list of IRs to plot
goodmoney.clipping <- T # apply goodmoney clipping?
do.clipping <- T #apply levels clipping?

#for poly model only
do.diffclip <- T #apply u-clipping?
minpoly_constraint <- 30 #Constraint on MMT: 25 or 30

#for spline model only
low <- 20 #low kink
high <- 25 #high kink
order.low <- 1 #order of low kink
order.high <- 3 #order of high kink

#set directory
wd <- "local" #"local" or "sacagawea"
dir <- ifelse(wd == "local", "/Users/trinettachong/Dropbox", "/local/shsiang/Dropbox")

csvv.dir <- paste0(dir,"/Global ACP/ClimateLaborGlobalPaper/Paper/Datasets/Trin_test/Mortality/timeseries/") #location of csvv
csvv.name <- ifelse(model == "poly", "Agespec_interaction_GMFD_POLY-4_TINV_CYA_NW_w1.csvv", paste0("Agespec_interaction_response_polyspline_",low,"C_",high,"C_order2_GMFD.csvv")) #name of csvv file
outputwd <- ifelse(wd == "local", paste0(csvv.dir, "response/year_responses/"), paste0(dir,"/Global ACP/MORTALITY/Replication_2018/3_Output/6_projection/regionmicroscopes/100_regions/")) #path for output
cov.dir <- paste0(dir, "/Global ACP/ClimateLaborGlobalPaper/Paper/Datasets/Trin_test/Mortality/mortality_impact_regions_tv_TINV_allyears.dta") #location of covariates
tas.path <- paste0(dir,"/Global ACP/ClimateLaborGlobalPaper/Paper/Datasets/Trin_test/Trin_test/prospectus-tools/gcp/validate/") #location of tas values (for plotting of histogram only, if plot.histogram == F, can ignore)

#------------------------------------------------------------------------------------------

#load covariates
df <- read.dta13(cov.dir)

#define function to plot response 
plot.response <- function(region){
  
  for (age in agelist){
    
    #read & parse csvv for gammas
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
    
    #create master df
    master <- data.frame()
    
    TT <- seq(-23, 41) #set up temperature range to plot response
    gammas <- sapply(csvv[3,], function(x) as.numeric(as.character(x))) #extract gammas
    
    for (yr in yearlist){
      
      #assign covariate values at T0 and T1
      climtas0 <- df$tmean[df$hierid == region & df$year == 2010] 
      loggdppc0 <- df$loggdppc[df$hierid == region & df$year == 2010] 
      climtas1 <- df$tmean[df$hierid == region & df$year == yr] 
      loggdppc1 <- df$loggdppc[df$hierid == region & df$year == yr] 
      
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
          
          if (do.clipping) { #levels-clipping
            yy0 <- get.curve(TT, gammas, climtas0, loggdppc0) 
            ii.min <- which.min(yy0[TT >= 10 & TT <= minpoly_constraint]) + which(TT == 10) - 1 
            #ii.min <- which.min(yy0[TT >= 10]) + which(TT == 10) - 1 
            print(TT[ii.min])
            
            yy1 <- get.curve(TT, gammas, climtas1, loggdppc1) 
            yy1 <- yy1 - yy1[ii.min]
            
            yyg <- get.curve(TT, gammas, climtas1, loggdppc0) #climate adapt only (No income adapt)
            yyg <- yyg - yyg[ii.min]
            
            if (goodmoney.clipping) {
              yy <- pmax(pmin(yy1, yyg), 0) # Good money and levels clipping
            } else {
              yy <- pmax(yy1, 0) # only levels clipping (no good money)
            }
            
            data.frame(name, TT, yy)
            
          } else { #no levels-clipping
            
            yy0 <- get.curve(TT, gammas, climtas0, loggdppc0) 
            ii.min <- which.min(yy0[TT >= 10 & TT <= minpoly_constraint]) + which(TT == 10) - 1 
            
            yy1 <- get.curve(TT, gammas, climtas1, loggdppc1)
            yy1 <- yy1 - yy1[ii.min]
            
            yyg <- get.curve(TT, gammas, climtas1, loggdppc0) #climate adapt only (No income adapt)
            yyg <- yyg - yyg[ii.min]
            
            if (goodmoney.clipping) {
              yy <- pmin(yy1, yyg) # Good money clipping only, no levels
            } else {
              yy <- yy1  # no Good money, no levels
            }
            
            data.frame(name, TT, yy)
            
          }
          
          
          if (do.diffclip) { #u-clipping
            yy.nd <- yy
            yy[ii.min:length(yy)] <- cummax(yy[ii.min:length(yy)]) #returns a vector with the cum max value ('max value to date')
            #yy[1:(ii.min-1)] <- rev(cummax(rev(yy[1:(ii.min-1)])))
            yy[1:(ii.min)] <- rev(cummax(rev(yy[1:(ii.min)])))
          } 
          
          data.frame(name, TT, yy) 
        }
      }
      
      meddf <- get.curvedf(paste0('RCP 8.5.',yr), sapply(csvv[3,], function(x) as.numeric(as.character(x))))
      meddf$temp <- seq(-23, 41)
      plotdf <- meddf #combine all 3 scenarios
      plotdf$year <- yr #add name column
      
      #set up filename
      u.suffix <- ifelse(do.diffclip==T, "_u", "")
      gm.suffix <- ifelse(goodmoney.clipping==T, "_goodmoney", "")
      l.suffix <- ifelse(do.clipping==T, "_levels", "")
      plotname <- ifelse(model == "poly", paste0("response-", region,"_",age,"_",yr,"_poly",u.suffix,l.suffix,gm.suffix,".pdf"), paste0("response-", region,"_",age,"_",yr,"_",low, "_", high,"_",order.low,"_",order.high,".pdf"))
      masterplotname <- ifelse(model == "poly", paste0("response-",region,"_",age,"_poly",u.suffix,l.suffix,gm.suffix,".pdf"), paste0("response-",age,"_",low, "_", high,"_",order.low,"_",order.high,".pdf"))
      
      #combine all years into single plot
      if (yr == yearlist[1]) {
        print("First year")
        master <- plotdf #if it is the year region in the list, assign to master
      } else {
        print(paste0("Plotting response curve for ", yr))
        master <- rbind(master, plotdf) #if it is not the 1st year in the list, rowbind with master
      }
    }
    
    #combine all years together
    print(paste0("Combining response curves for all years for ", region, age))
    
    if (age=="oldest"){
      labelyaxis <- 100
      y.lim <- c(-20,40)
    } else if (age=="young") {
      labelyaxis <- 7.5
      y.lim <- c(-2,2)
    } else {
      labelyaxis <- 1
      y.lim <- c(-2,4)
    }
    
    p <- ggplot(master, aes(x = temp, y = yy, group = year)) +
      geom_line(aes(colour=year), size = 1) +
      geom_line(aes(colour=year), size = 1) +
      geom_hline(yintercept=0, size=.2) + #zeroline
      theme_minimal() +  
      ylab("Change in deaths / 100,000") +
      coord_cartesian(ylim = y.lim)  +
      scale_x_continuous(expand=c(0, 0)) +
      scale_linetype_discrete(name=NULL) +
      scale_color_viridis(option="magma") 
      ggsave(paste0(outputwd, masterplotname), width = 10, height = 10) #plot response function 
    
    # plot histograms
    if (plot.histogram){
      
      tas <- read.csv(paste0(tas.path,"tas-dists.csv"))
      row0 <- which(tas$hierid==region)[1]
      
      temp.low <- as.numeric(substr(names(tas)[4], nchar(names(tas))[4] - 1, nchar(names(tas)[4]))) + 0.5
      temp.high <- as.numeric(substr(names(tas)[length(tas)], 4,5)) + 0.5
      
      if(substr(names(tas)[3], 4,4) == "."){ #if temperature in tas-dists range from negative numbers
        temps <- seq(-temp.low, temp.high)
      } else{
        temps <- seq(temp.low-1, temp.high)
      }
      
      #temps <- seq(-23, 41)
      
      regtas <- data.frame(group=rep(c('Historical', 'RCP 8.5 2095'), each=length(temps)),
                           temps=rep(temps, 2),
                           counts=c(t(tas[row0, -(1:2)]) / sum(t(tas[row0, -(1:2)])),
                                    t(tas[row0+1, -(1:2)]) / sum(t(tas[row0+1, -(1:2)]))))
      regtas$group <- factor(regtas$group, c('RCP 8.5 2095', 'Historical'))
      
      p_hist <- ggplot(regtas, aes(temps, counts, fill=group)) +
        geom_bar(stat="identity", position="dodge") + 
        theme_minimal() +
        scale_x_continuous(expand=c(0, 0)) + 
        ylab("Portion of days") + xlab("Daily temperature (C)") +
        coord_cartesian(xlim =c(-22.5,47))  +
        scale_fill_manual(values = c("#FBC17D", "#81176D"), 
                          name=NULL) +
        theme(legend.justification=c(1,1), legend.position=c(1,1))
      #ggsave(paste0(outputwd,"weather-", tas[row0, 1], ".pdf"), width=5, height=2.5) #plot histogram alone
      
      g <- arrangeGrob(p, p_hist, nrow=2) #generates new combined plot
      ggsave(filename=paste0(outputwd,masterplotname), width = 10, height = 12, g) #plot response function and histogram
    }
    
    
  }
}


lapply(regionlist, plot.response)  #apply plot.response function to impact regions in regionlist



