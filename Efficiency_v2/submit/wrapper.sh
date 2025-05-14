#!/bin/bash

# setup environment
cd ${CMSSW_BASE}/src/
cmsenv
cd myAnalyzers/bph-hlt-tools/Efficiency_v2

export X509_USER_PROXY=X509_USER_PROXY

# execute the script
python3 cutNcount_efficiency.py \
  --data tagtuples_HLT_Mu8_v_MC_Jpsito2Mu_pythia8_2022EE_v4.json \
  --selection mediumID_selection_L1.json \
  --output condor_test/