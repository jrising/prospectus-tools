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
    toaggregate = 0
    
    for batch, rcp, model, iam, ssp, targetdir in iterator:
        status = None
        for model in models:
            for variation in variations:
                if not check_doit(True, targetdir, model + variation, ''):
                    status = 'incomplete'
                    break
                
                for aggregate in aggregated:
                    if not os.path.exists(model + variation + aggregate + '.nc4'):
                        status = 'toaggregate'
                        break

                if status is not None:
                    break
            if status is not None:
                break

        if status == 'incomplete':
            incomplete += 1
        elif status == 'toaggregate':
            toaggregate += 1
        else:
            complete += 1

    return complete, incomplete, toaggregate

print "Monte Carlo:"
complete, incomplete, toaggregate = results.iterate_montecarlo("/shares/gcp/outputs/labor/impacts-andrena")
print complete, incomplete, toaggregate

print "Median"
complete, incomplete, toaggregate = results.iterate_batch("/shares/gcp/outputs/labor/impacts-andrena", 'median')
print complete, incomplete, toaggregate
