echo "-- setting proxies --"
voms-proxy-init --voms cms --valid 168:00
echo "-- source CRAB3 --"
source /cvmfs/cms.cern.ch/crab3/crab.sh
