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
    missingness = 0
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
                    if not os.path.exists(os.path.join(targetdir, model + variation + '.nc4')):
                        status = 'missingness'
                        continue

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
                        if '-brc' in targetdir or '-osdc' in targetdir:
                            os.remove(os.path.join(targetdir, model + variation + aggregate + '.nc4'))
                        status = 'toaggregate'
                        break

                if status is not None and status != 'missingness':
                    break
            if status is not None and status != 'missingness':
                break

        if status == 'incomplete':
            incomplete += 1
        elif status == 'toaggregate':
            toaggregate += 1
        else:
            with open(os.path.join(targetdir, "COMPLETE"), 'w') as fp:
                fp.write("2016-12-23")
            if status == 'missingness':
                missingness += 1
            else:
                complete += 1

    sys.stdout = stdout_

    return complete, missingness, incomplete, toaggregate, stream.getvalue()

models = ['global_interaction_gmfd', 'global_interaction_no_popshare_gmfd'] # 'global_interaction_best', 'global_interaction_no_popshare_best', 
variations = ['', '_comatose', '_dumb', '-histclim', '-costs']
aggregated = ['-aggregated', '-levels']

print "Mortality Median 2:"
iterator = results.iterate_batch("/shares/gcp/outputs/mortality/impacts-pharaoh2", 'median')
complete, missingness, incomplete, toaggregate, output4 = count_results(iterator, mortality.allmodels.check_doit)

print complete, missingness, incomplete, toaggregate

print "Mortality Monte Carlo 2:"
iterator = results.iterate_montecarlo("/shares/gcp/outputs/mortality/impacts-pharaoh2")
complete, missingness, incomplete, toaggregate, output3 = count_results(iterator, mortality.allmodels.check_doit)
print complete, missingness, incomplete, toaggregate

print "Mortality Median:"
iterator = results.iterate_batch("/shares/gcp/outputs/mortality/impacts-pharaoh", 'median')
complete, missingness, incomplete, toaggregate, output4 = count_results(iterator, mortality.allmodels.check_doit)

print complete, missingness, incomplete, toaggregate

print "Mortality Monte Carlo:"
iterator = results.iterate_montecarlo("/shares/gcp/outputs/mortality/impacts-pharaoh")
complete, missingness, incomplete, toaggregate, output3 = count_results(iterator, mortality.allmodels.check_doit)
print complete, missingness, incomplete, toaggregate

models = ['labor_global_interaction_best_13dec']
variations = ['', '_comatose', '_dumb', '-histclim']
aggregated = ['-aggregated', '-levels']

print "Labor Monte Carlo:"
iterator = results.iterate_montecarlo("/shares/gcp/outputs/labor/impacts-andrena")
complete, missingness, incomplete, toaggregate, output1 = count_results(iterator, lambda redocheck, targetdir, basename, suffix: labor.allmodels.check_doit(redocheck, targetdir, basename, suffix, deletebad=('-brc' in targetdir or '-osdc' in targetdir)))
print complete, missingness, incomplete, toaggregate

print "Labor Median:"
iterator = results.iterate_batch("/shares/gcp/outputs/labor/impacts-andrena", 'median')
complete, missingness, incomplete, toaggregate, output2 = count_results(iterator, lambda redocheck, targetdir, basename, suffix: labor.allmodels.check_doit(redocheck, targetdir, basename, suffix, deletebad=('-brc' in targetdir or '-osdc' in targetdir)))
print complete, missingness, incomplete, toaggregate
