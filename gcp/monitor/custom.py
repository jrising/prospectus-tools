import os, sys
sys.path.append("../extract/lib")
sys.path.append("~/projects/gcp/impact-calculations/impacts/labor")

import results
import allmodels

models = ['labor_global_interaction_best_13dec']
variations = ['', '_comatose', '_dumb', '-histclim']
aggregated = ['-aggregated', '-levels']

def count_results(iterator):
    complete = 0
    incomplete = 0
    
    for batch, rcp, model, iam, ssp, targetdir in iterator:
        is_incomplete = False
        for model in models:
            for variation in variations:
                if not check_doit(True, targetdir, model + variation, ''):
                    is_incomplete = True
                    break
                
                for aggregate in aggregated:
                    if not os.path.exists(model + variation + aggregate + '.nc4'):
                        is_incomplete = True
                        break

                if is_incomplete:
                    break
            if is_incomplete:
                break

        if is_incomplete:
            incomplete += 1
        else:
            complete += 1

    return complete, incomplete

print "Monte Carlo:"
complete, incomplete = results.iterate_montecarlo("/shares/gcp/outputs/labor/impacts-andrena")
print complete, incomplete

print "Median"
complete, incomplete = results.iterate_batch("/shares/gcp/outputs/labor/impacts-andrena", 'median')
print complete, incomplete
