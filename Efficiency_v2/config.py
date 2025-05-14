# configuration for default effieciency selection
import numpy as np

eta_barrel  = [0.0, 0.9]
eta_overlap = [0.9, 1.2]
eta_endcap  = [1.2, 2.4]
eta_bins = {
    'cms' : [eta_barrel[0], eta_endcap[1]],
    'barrel'  : eta_barrel,
    'overlap' : eta_overlap,
    'endcap'  : eta_endcap,
}
deltaR_bins = {
    'dRincl': [0.00, 1.20],
    'dR_1'  : [0.00, 0.45],
    'dR_2'  : [0.45, 0.60],
    'dR_3'  : [0.60, 1.20],
}


# default binning
Bins1d = dict(
    DiMu_mu2_pt  = [0,1,2,3,4,5,6,7,8,9,10,12,14,16,18,20,25,30,50], #[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,25,30,50],
    DiMu_mu2_eta = [-2.4, -1.2, -0.9, 0.9, 1.2, 2.4],#np.linspace(-2.4, 2.4, 11),
    DiMu_mu1_eta = np.linspace(-2.4, 2.4, 24),
    DiMu_mass    = [2.9,2.95, 3, 3.05, 3.1, 3.15 ,3.2, 3.25, 3.3],
    DiMu_mu2_phi = np.linspace(-np.pi, np.pi, 10),
    DiMu_dR      = [0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5,  0.7],
    L1_mu1_dR    = np.linspace(0, 1.0, 40),
    L1vtx_mu1_dR = np.linspace(0, 0.4, 50),
    L1_mu2_dR    = np.linspace(0, 1.0, 40),
    L1vtx_mu2_dR = np.linspace(0, 0.4, 60),
    lxySig       = [0, 0.5, 1, 1.5, 2, 2.5, 3,  3.5, 4, 4.5, 5, 5.5]
)
Bins1d_tight = dict(
    DiMu_mu2_pt = [0,4,5,6,7,8,9,10,12,14,16,18,20,25,30,50]
)
pretty_name=dict(
    DiMu_mu2_pt = "probe #mu p_{T} (GeV)",
    DiMu_mu2_eta = "probe #mu_{#eta}",
    DiMu_mu1_pt = "tag #mu p_{T} (GeV)",
    DiMu_mu1_eta = "tag #mu_{#eta}",
    DiMu_mass = "M(#mu_{T}#mu_{P}) (GeV)",
    DiMu_mu2_phi = r'Offline $\mu_{\phi}$',
    DiMu_dR="#Delta R(#mu_{tag}, #mu_{probe})",
    L1_mu1_dR = "#Delta R(#mu_{tag}, L1_{tag})",
    L1vtx_mu1_dR = "#Delta R(#mu_{tag}, L1vtx_{tag})",
    L1_mu2_dR = "#Delta R(#mu_{probe}, L1_{probe})",
    L1vtx_mu2_dR = "#Delta R(#mu_{probe}, L1vtx_{probe})",
    lxySig = "L_{xy}/#sigma ",
)

variables = ['mu2_pt', 'mu2_eta', 'DiMu_mass', 'mu2_phi', 'DiMu_dR', 'lxySig']
variables = ['DiMu_mu2_pt']

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