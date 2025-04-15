# -- MC--
python3 cutNcount_efficiency.py --data data/tagtuples_HLT_Mu8_v_MC_Jpsito2Mu_pythia8_2023.json --selection selection/baselineBPHselection.json           --output results/ --splitEta
# -- DATA --
python3 cutNcount_efficiency.py --data data/tagtuples_HLT_Mu8_v_DataMuon_2023.json --selection selection/baselineBPHselection.json           --output results/ --splitEta
# -- scale factors --
python3 scale_factors.py --data results/efficiency_Muon_Run2023_L1match_bph_sel.root      --mc results/efficiency_Jpsito2Mu_pythia8_Run2023_L1match_bph_sel.root      --output results/scaleFactors_Run2023_bph_sel
python3 scale_factors.py --data results/efficiency_Muon_Run2023_L1match_bph_sel.root      --mc results/efficiency_Jpsito2Mu_pythia8_Run2023_L1match_bph_sel.root      --output results/scaleFactors_Run2023_barrel_bph_sel --eta_region barrel
python3 scale_factors.py --data results/efficiency_Muon_Run2023_L1match_bph_sel.root      --mc results/efficiency_Jpsito2Mu_pythia8_Run2023_L1match_bph_sel.root      --output results/scaleFactors_Run2023_overlap_bph_sel --eta_region overlap
python3 scale_factors.py --data results/efficiency_Muon_Run2023_L1match_bph_sel.root      --mc results/efficiency_Jpsito2Mu_pythia8_Run2023_L1match_bph_sel.root      --output results/scaleFactors_Run2023_endcap_bph_sel --eta_region endcap
