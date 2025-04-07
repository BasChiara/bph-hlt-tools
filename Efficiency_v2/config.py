# configuration for default effieciency selection
import numpy as np


Bins1d = dict(
    DiMu_mu2_pt  = [0,1,2,3,4,5,6,7,8,9,10,12,14,16,18,20,25,30,40,50],
    DiMu_mu2_eta = [-2.4, -1.2, -0.9, 0.9, 1.2, 2.4],#np.linspace(-2.4, 2.4, 11),
    DiMu_mass   = [2.9,2.95, 3, 3.05, 3.1, 3.15 ,3.2, 3.25, 3.3],
    DiMu_mu2_phi = np.linspace(-np.pi, np.pi, 10),
    DiMu_dR     = [0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5,  0.7],
    lxySig      = [0, 0.5, 1, 1.5, 2, 2.5, 3,  3.5, 4, 4.5, 5, 5.5]
)
pretty_name=dict(
    DiMu_mu2_pt = "probe #mu p_{T} (GeV)",
    DiMu_mu2_eta = r'Offline $\mu_{\eta}$',
    DiMu_mass = "M(#mu_{T}#mu_{P}) (GeV)",
    DiMu_mu2_phi = r'Offline $\mu_{\phi}$',
    DiMu_dR="$\Delta R(\mu_{tag}, \mu_{probe})$",
)

variables = ['mu2_pt', 'mu2_eta', 'DiMu_mass', 'mu2_phi', 'DiMu_dR', 'lxySig']
variables = ['DiMu_mu2_pt', 'DiMu_dR']

default_tagQuery = ' & '.join([
        "(2.9<DiMu_mass<3.3)",
        "(DiMu_Prob>0.005)",
        "(abs(muTag_eta)<2.4) & (abs(mu2_eta)<2.4)",
        "(muTag_pt>8)",
        "(muTag_L1_match==1)",
        "(muTag_charge+mu2_charge==0)",
        "(muTagGlobal==1) & (mu2Global==1)",
        "(muTagloose==1)  & (mu2loose==1)",
])

default_probeQuery = ' & '.join([
    "",
])
L1_tag_path = 'HLT_Mu8_v'
L1_probe_path = 'HLT_Mu0_L1DoubleMu_v'

HLT_tag_path = 'HLT_Mu8_v'
HLT_probe_path = 'HLT_Mu0_L1DoubleMu_v'

L1_seeds = ['L1_DoubleMu0er1p4_SQ_OS_dEta_Max1p2',
            'L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6',
            'L1_DoubleMu5_SQ_OS_dR_Max1p6',
            'L1_DoubleMu3er2p0_SQ_OS_dR_Max1p6',
            'L1_DoubleMu0er1p5_SQ_OS_dEta_Max1p2',
            'L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p6',
            'L1_DoubleMu0er1p4_OQ_OS_dEta_Max1p6',
            'L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p5',
            'L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4',
            'L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4',
            'L1_DoubleMu4p5_SQ_OS_dR_Max1p2',
            'L1_DoubleMu4_SQ_OS_dR_Max1p2', 
            'L1_DoubleMu3er2p0_SQ_OS_dR_Max1p4',
            
            'L1_DoubleMu0er1p5_SQ_dR_Max1p4',
            'L1_DoubleMu0er2p0_SQ_dEta_Max1p6',
            'L1_DoubleMu0er2p0_SQ_dEta_Max1p5',

            'L1_SingleMu10_SQ14_BMTF',
            'L1_SingleMu11_SQ14_BMTF',
            'L1_SingleMu0_BMTF',
]

L1_seeds_group = {
    'L1_DoubleMu0er*_SQ_OS_dEta_Max*' : ['L1_DoubleMu0er1p4_SQ_OS_dEta_Max1p2',
                                            'L1_DoubleMu0er1p5_SQ_OS_dEta_Max1p2',
                                            'L1_DoubleMu0er1p4_SQ_OS_dEta_Max1p6',
                                            'L1_DoubleMu0er1p5_SQ_OS_dEta_Max1p6',
                                         ]
}