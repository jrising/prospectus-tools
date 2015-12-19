DMAS_HOME = /home/jrising/aggregator/trunk
DMAS_ENV = /home/jrising/aggregator/env

source $DMAS_ENV/bin/activate
paster request $DMAS_HOME/Aggregator/production.ini /acra/make_single weatherdir=$1 scenario=${2-rcp85} pval=${3-.5}
