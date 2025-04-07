# -- MC--
#python3 cutNcount_efficiency.py --data data/tagtuples_HLT_Mu8_v_MC_Jpsito2Mu_pythia8_2023.json --selection selection/baselineBPHselection_noL1.json      --output results/
#python3 cutNcount_efficiency.py --data data/tagtuples_HLT_Mu8_v_MC_Jpsito2Mu_pythia8_2023.json --selection selection/baselineBPHselection_noL1probe.json --output results/
#python3 cutNcount_efficiency.py --data data/tagtuples_HLT_Mu8_v_MC_Jpsito2Mu_pythia8_2023.json --selection selection/baselineBPHselection.json           --output results/
# -- DATA --
python3 cutNcount_efficiency.py --data data/tagtuples_HLT_Mu8_v_DataMuon_2023_pTbias.json --selection selection/baselineBPHselection_noL1.json      --output results/
python3 cutNcount_efficiency.py --data data/tagtuples_HLT_Mu8_v_DataMuon_2023_pTbias.json --selection selection/baselineBPHselection_noL1probe.json --output results/
python3 cutNcount_efficiency.py --data data/tagtuples_HLT_Mu8_v_DataMuon_2023_pTbias.json --selection selection/baselineBPHselection.json           --output results/
# -- scale factors --
#python3 scale_factors.py --data results/efficiency_Muon_Run2023_test_bph_selNOl1tagprobe.root      --mc results/efficiency_Jpsito2Mu_pythia8_Run2023_test_bph_selNOl1tagprobe.root      --output results/scaleFactors_Run2023_test_bph_selNOl1tagprobe
#python3 scale_factors.py --data results/efficiency_Muon_Run2023_test_bph_selNOl1probe.root      --mc results/efficiency_Jpsito2Mu_pythia8_Run2023_test_bph_selNOl1probe.root      --output results/scaleFactors_Run2023_test_bph_selNOl1probe
#python3 scale_factors.py --data results/efficiency_Muon_Run2023_test_bph_sel.root      --mc results/efficiency_Jpsito2Mu_pythia8_Run2023_test_bph_sel.root      --output results/scaleFactors_Run2023_test_bph_sel


#python3 cutNcount_efficiency.py --data data/tagtuples_HLT_Mu8_v_MC_Jpsito2Mu_pythia8_2023.json --selection selection/baselineBPHselection_L1den.json           --output results/
#python3 cutNcount_efficiency.py --data data/tagtuples_HLT_Mu8_v_DataMuon_2023.json             --selection selection/baselineBPHselection_L1den.json           --output results/