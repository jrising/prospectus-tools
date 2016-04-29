import os, sys
from lib import configs

command = "python single.py \"%s\" %s %s > %s"

region = sys.argv[1]
column = sys.argv[2]

destination = column + '-' + region
os.mkdir(destination)

for filepath in sys.argv[3:]:
    outfile = filepath[:-4] + '.csv'

    print filepath
    os.system(command % (filepath, region, column, os.path.join(destination, os.path.basename(outfile))))

