

SELECTION=("config_TnPselection/BPH_selection.json" "config_TnPselection/GM_DRmuL1_0p3_selection.json")
SELECTION=("config_TnPselection/BPH_selection.json")

# BuToJpsiK_ToMuMu
TAGTUPLES="config_TagTuples/tagtuplesHLT_Mu8_v_MC_BuToJpsiK_Run3.json"
for SEL in ${SELECTION[@]}; do
    python3 scripts/to_run_customSelection.py --in_tagtuples $TAGTUPLES --tnp_selection $SEL
done

# Inclusive Dilepton Minimum Bias
TAGTUPLES="config_TagTuples/tagtuplesHLT_Mu8_v_MC_InclusiveDileptonMinBias2022.json"
for SEL in ${SELECTION[@]}; do
    python3 scripts/to_run_customSelection.py --in_tagtuples $TAGTUPLES --tnp_selection $SEL
done

# Jpsi to 2 muons
TAGTUPLES="config_TagTuples/tagtuplesHLT_Mu8_v_MC_Jpsito2Mu_pythia8_2023.json"
for SEL in ${SELECTION[@]}; do
    python3 scripts/to_run_customSelection.py --in_tagtuples $TAGTUPLES --tnp_selection $SEL
done