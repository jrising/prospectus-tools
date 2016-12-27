echo "BRC Mortality:"
rsync -avz "dtn.brc.berkeley.edu:/global/scratch/jrising/outputs/mortality/impacts-pharaoh/*" /shares/gcp/outputs/mortality/impacts-pharaoh/brc/
echo "BRC Labor:"
rsync -avz "dtn.brc.berkeley.edu:/global/scratch/jrising/outputs/labor/impacts-andrena/*" /shares/gcp/outputs/labor/impacts-andrena/brc/
echo "OSDC Mortality:"
rsync -avz "griffinvm:/mnt/gcp/outputs/mortality/impacts-pharaoh/*" /shares/gcp/outputs/mortality/impacts-pharaoh/osdc/
echo "OSDC Labor:"
rsync -avz "griffinvm:/mnt/gcp/outputs/labor/impacts-andrena/*" /shares/gcp/outputs/labor/impacts-andrena/osdc/
