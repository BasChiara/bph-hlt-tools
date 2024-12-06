# configuration for default effieciency selection
import numpy as np


Bins1d = dict(
    muProbe_pt = [0,1,2,3,4,5,6,7,8,9,10,12,14,16,18,20,25,30,40,50],
    muProbe_eta = np.linspace(-2.4, 2.4, 11),
    DiMu_mass = [2.9,2.95, 3, 3.05, 3.1, 3.15 ,3.2, 3.25, 3.3],
    muProbe_phi = np.linspace(-np.pi, np.pi, 20),
    dR_muons = [0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5,  0.7],
    lxySig = [0, 0.5, 1, 1.5, 2, 2.5, 3,  3.5, 4, 4.5, 5, 5.5]
)
pretty_name=dict(
    muProbe_pt = r'Offline $\mu_{pT}$',
    muProbe_eta = r'Offline $\mu_{\eta}$',
    DiMu_mass = r'$m_{\mu\mu}$',
    muProbe_phi = r'Offline $\mu_{\phi}$',
    dR_muons="$\Delta R(\mu_{tag}, \mu_{probe})$",
)

variables = ['muProbe_pt', 'muProbe_eta', 'DiMu_mass', 'muProbe_phi', 'dR_muons', 'lxySig']

default_tagQuery = ' & '.join([
        "(2.9<DiMu_mass<3.3)",
        "(DiMu_Prob>0.005)",
        "(abs(muTag_eta)<2.4) & (abs(muProbe_eta)<2.4)",
        "(muTag_pt>8)",
        "(muTag_L1_match==1)",
        "(muTag_charge+muProbe_charge==0)",
        "(muTagGlobal==1) & (muProbeGlobal==1)",
        "(muTagloose==1)  & (muProbeloose==1)",
])

default_probeQuery = ' & '.join([
    "(muProbe_L1_match==1)",
])
L1_tag_path = 'HLT_Mu8_v'
L1_probe_path = 'HLT_Mu0_L1DoubleMu_v'
HLT_tag_path = 'HLT_Mu8_v'
HLT_probe_path = 'HLT_Mu0_L1DoubleMu_v'