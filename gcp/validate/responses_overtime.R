#------------------------------------------------------------------------------------------
# IR responses overtime

# This script plots the response function(s) of impact region(s) over time.

# Sector: Energy
# Updated 8 Jan 2019 by Maya Norman

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

model <- "TINV_clim" #poly or spline
clim_data <- "GMFD_v3" #BEST
#Define Income Group Bounds
if (model == "TINV_clim" & clim_data == "GMFD_v3") {
  IG1_upper = 9.128 #7th term in incbin from model config
  IG2_upper = 9.873 #9th term in incbin from model config
}

yearlist <- seq(2010, 2099) #define time period to plot response functions
plot.histogram <- F #plot histogram below response?
regionlist <- list("USA.14.608", "USA.33.1833", "USA.3.103", "USA.3.102", "USA.3.101") #define list of IRs to plot

#set directory
wd <- "local" #"local" or "sacagawea"
dir <- ifelse(wd == "local", "/Users/mayanorman/Dropbox/", "/home/manorman/")

csvv.dir <- paste0(dir,"GCP_Reanalysis/ENERGY/IEA_Replication/Projection/eel_projection/",clim_data,"/data/csvv/",model, "/") #location of csvv
csvv.name <- paste0('FD_FGLS_inter_',clim_data,'_poly2_COMPILE_total_energy_',model,'.csv') #name of csvv file
outputwd <- paste0(dir,"GCP_Reanalysis/ENERGY/IEA_Replication/Projection/eel_projection/",clim_data,"/output/",model,"/") #path for output
cov.dir <- paste0(dir, "GCP_Reanalysis/ENERGY/IEA/Yuqi_Codes/Data/covars_TINV_clim_1218.dta") #location of covariates
tas.path <- paste0(dir,"prospectus-tools/gcp/validate/") #location of tas values (for plotting of histogram only, if plot.histogram == F, can ignore)

#------------------------------------------------------------------------------------------

#load covariates
df <- read.dta13(cov.dir)

#Step 1: Define helper functions ------------------------------------------------------------------------

#income group function (takes in loggdppc and spits out income group)
get.incGroup <- function(loggdppc) {
  if(loggdppc <= IG1_upper) {
    c(1,'incbin1')
  } else if (loggdppc > IG1_upper & loggdppc <= IG2_upper) {
    c(2, 'incbin7')
  } else if (loggdppc > IG2_upper) {
    c(3, 'incbin9')
  }
}

#return coefficent based on clim var and covariate
get.coefficient <- function(coefs, csvv, pred, covar) coefs[csvv[1,] == pred & csvv[2,] == covar]

#Sketch out the response curve
get.curve <- function(TT, above20, below20, coefs, csvv, cdd, hdd, incgroup) { 
  
  if (model == "TINV_clim"){
    
    beta1 <- get.coefficient(coefs, csvv, 'tas', incgroup[[2]]) 
    beta2 <- get.coefficient(coefs, csvv, 'tas2', incgroup[[2]]) 
    
    gamma1 <- get.coefficient(coefs, csvv, 'tas-cdd-20', paste0("climtas-cdd-20*",incgroup[[2]]))*cdd 
    gamma2 <- get.coefficient(coefs, csvv, 'tas-cdd-20-poly-2', paste0("climtas-cdd-20*",incgroup[[2]]))*cdd 
    
    lambda1 <- get.coefficient(coefs, csvv, 'tas-hdd-20', paste0("climtas-hdd-20*",incgroup[[2]]))*hdd 
    lambda2 <- get.coefficient(coefs, csvv, 'tas-hdd-20-poly-2', paste0("climtas-hdd-20*",incgroup[[2]]))*hdd 
    
    beta <- beta1 * (TT-20) + beta2 * (TT^2 - 400) 
    gamma <- gamma1 * (TT - 20) * above20 + gamma2 * (TT^2 - 400) * above20
    lambda <- lambda1 * (20 - TT) * below20 + lambda2 * (400 - TT^2) * below20
    
    response <- beta + gamma + lambda
    
    data.frame(TT,response)
    
  }
}

#define function to plot response 
plot.response <- function(region){
    
  adapt <- "fulladapt"
  #Part a: Read in and Clean CSVV ---------------------------------------------------------------------------
    #read & parse csvv for gammas
    skip.no <- 21 #lines to skip when loading csvv, 18 for poly4, 16 for hddcdd 
    csvv <- read.csv(paste0(csvv.dir, csvv.name), skip = skip.no, header = F, sep= ",", stringsAsFactors = T)
    
    squish_function <- stringr::str_squish #str_squish function doesn't work on sacagawea
    
    #subset to relevant rows & remove blank spaces in characters
    csvv <- csvv[-c(2,4,6, nrow(csvv)-1, nrow(csvv)), ] %>%
      rowwise() %>%
      mutate_all(funs(squish_function(.))) %>%
      ungroup()
  #----------------------------------------------------------------------------------------------------------

  #Part b: Gather Supplies for Plotting Yearly Response Function --------------------------------------------------
    
    #create master df to be filled with temp and response
    master <- data.frame()
    
    #set up temperature range to plot response
    TT <- seq(-23, 41) 
    above20 <-ifelse(TT>=20, 1, 0)
    below20 <-ifelse(TT<20, 1, 0)
    
    #Take simply the coefficient row out of the csvv
    coefs <- sapply(csvv[3,], function(x) as.numeric(as.character(x))) #extract gammas

    for (yr in yearlist){
      
      #assign covariate values at T0 and T1
      climtascdd0 <- df$climtascdd20[df$region == region & df$year == 2010] 
      climtashdd0 <- df$climtashdd20[df$region == region & df$year == 2010] 
      loggdppc0 <- df$loggdppc[df$region == region & df$year == 2010] 
      incGroup0 <- get.incGroup(loggdppc0) 
      
      climtascdd1 <- df$climtascdd20[df$region == region & df$year == yr] 
      climtashdd1 <- df$climtashdd20[df$region == region & df$year == yr] 
      loggdppc1 <- df$loggdppc[df$region == region & df$year == yr] 
      incGroup1 <- get.incGroup(loggdppc1) 
      
      if (adapt == "fulladapt") {
        plot_df <- get.curve(TT, above20, below20, coefs, csvv, climtascdd1, climtashdd1, incGroup1)
      } else if (adapt == "incadapt") {
        plot_df <- get.curve(TT, above20, below20, coefs, csvv, climtascdd0, climtashdd0, incGroup1)
      } else if (adapt == "noadapt") {
        plot_df <- get.curve(TT, above20, below20, coefs, csvv, climtascdd0, climtashdd0, incGroup0)
      } else if (adapt == "climadapt") {
        plot_df <- get.curve(TT, above20, below20, coefs, csvv, climtascdd1, climtashdd1, incGroup0)
      }
      
      plot_df$year <- yr #add name column
      plot_df$adaptation <- adapt
      
      #combine all years into single plot
      if (yr == yearlist[1]) {
        print("First year")
        master <- plot_df #if it is the year region in the list, assign to master
      } else {
        print(paste0("Plotting response curve for ", yr))
        master <- rbind(master, plot_df) #if it is not the 1st year in the list, rowbind with master
      }
    }
    
    #combine all years together
    print(paste0("Combining response curves for all years for ", region, adapt))
    
    p <- ggplot(master, aes(x = temp, y = yy, group = year)) +
      geom_line(aes(colour=year), size = 1) +
      geom_line(aes(colour=year), size = 1) +
      geom_hline(yintercept=0, size=.2) + #zeroline
      theme_minimal() +  
      ylab("kWh pc") +
      coord_cartesian(ylim = c(-20,100))  +
      scale_x_continuous(expand=c(0, 0)) +
      scale_linetype_discrete(name=NULL) +
      scale_color_viridis(option="magma") 
      ggsave(paste0(outputwd, "response_curves_", adapt, "_", region), width = 10, height = 10) #plot response function 
    
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
      ggsave(filename=paste0(outputwd, "response_curves_", adapt, "_", region), width = 10, height = 12, g) #plot response function and histogram
    } 
  }

#---------------------------------------------------------------------------------------------------------------------------

#Step 2: Apply functions to regionlist

lapply(regionlist, plot.response)  #apply plot.response function to impact regions in regionlist



