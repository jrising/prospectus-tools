import os, sys, cStringIO
sys.path.append("../extract/lib")
sys.path.append("../../../../../projects/gcp/impact-calculations")

import results
from impacts import labor, mortality
from generate import checks

def count_results(iterator, check_doit):
    stdout_ = sys.stdout
    sys.stdout = stream = cStringIO.StringIO()

    complete = 0
    incomplete = 0
    toaggregate = 0
    failures = {} # {message -> targetdir}
    
    for batch, rcp, model, iam, ssp, targetdir in iterator:
        status = None
        for model in models:
            for variation in variations:
                if variation == '-costs':
                    if not os.path.exists(os.path.join(targetdir, model + variation + '.nc4')):
                        status = 'toaggregate'
                        break
                else:
                    if check_doit(True, targetdir, model + variation, ''):
                        status = 'incomplete'
                        break
                
                for aggregate in aggregated:
                    if not os.path.exists(os.path.join(targetdir, model + variation + aggregate + '.nc4')):
                        print "Missing", os.path.join(targetdir, model + variation + aggregate + '.nc4')
                        status = 'toaggregate'
                        break

                    if variation != '-costs' and not checks.check_result_100years(os.path.join(targetdir, model + variation + aggregate + '.nc4'), regioncount=5665):
                        print "Failed aggregate", os.path.join(targetdir, model + variation + aggregate + '.nc4')
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
            with open(os.path.join(targetdir, "COMPLETE"), 'w') as fp:
                fp.write("2016-12-23")
            complete += 1

    sys.stdout = stdout_

    return complete, incomplete, toaggregate, stream.getvalue()

models = ['labor_global_interaction_best_13dec']
variations = ['', '_comatose', '_dumb', '-histclim']
aggregated = ['-aggregated', '-levels']

print "Labor Monte Carlo:"
iterator = results.iterate_montecarlo("/shares/gcp/outputs/labor/impacts-andrena")
complete, incomplete, toaggregate, output1 = count_results(iterator, labor.allmodels.check_doit)
print complete, incomplete, toaggregate

print "Labor Median:"
iterator = results.iterate_batch("/shares/gcp/outputs/labor/impacts-andrena", 'median')
complete, incomplete, toaggregate, output2 = count_results(iterator, labor.allmodels.check_doit)
print complete, incomplete, toaggregate

models = ['global_interaction_best', 'global_interaction_gmfd', 'global_interaction_no_popshare_best', 'global_interaction_no_popshare_gmfd']
variations = ['', '_comatose', '_dumb', '-histclim', '-costs']
aggregated = ['-aggregated', '-levels']

print "Mortality Monte Carlo:"
iterator = results.iterate_montecarlo("/shares/gcp/outputs/mortality/impacts-pharaoh")
complete, incomplete, toaggregate, output3 = count_results(iterator, mortality.allmodels.check_doit)
print complete, incomplete, toaggregate

print "Mortality Median:"
iterator = results.iterate_batch("/shares/gcp/outputs/mortality/impacts-pharaoh", 'median')
complete, incomplete, toaggregate, output4 = count_results(iterator, mortality.allmodels.check_doit)
print complete, incomplete, toaggregate

