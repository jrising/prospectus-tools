python quantiles.py configs/covariates.yml --column=tas Covariates-aggregated
python quantiles.py configs/covariates.yml --column=loggdppc Covariates-aggregated
python quantiles.py configs/covariates.yml --column=logpopop Covariates-aggregated
python quantiles.py configs/covariates-mortality.yml MLE_splines_GMFD_03212017-aggregated -MLE_splines_GMFD_03212017-histclim-aggregated
#python quantiles.py configs/covariates-mortality2.yml global_interaction_gmfd-aggregated
