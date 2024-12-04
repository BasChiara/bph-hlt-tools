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

HLT_Paths=[ "HLT_DoubleMu4_3_LowMass_v",
            "HLT_DoubleMu4_3_LowMass_SS_v",
            "HLT_DoubleMu4_LowMass_Displaced_v",
            "HLT_DoubleMu4_MuMuTrk_Displaced_v",
            "HLT_DoubleMu4_3_Bs_v",
            "HLT_Dimuon10_y1p4_v", # This may not be in the menu!
            "HLT_DoubleMu4_3_Jpsi_v",
            "HLT_Mu8_v", 
            "HLT_IsoMu24_v",
            "HLT_IsoMu27_v",
            "HLT_Mu4_L1DoubleMu_v",
            "HLT_Mu0_L1DoubleMu_v",
            "HLT_Mu3_PFJet40_v",
            "HLT_Mu15_v",
            "HLT_DoubleMu2_Jpsi_LowPt_v",
            "HLT_Dimuon10_Upsilon_y1p4_v",

            "HLT_Mu0_Barrel_v",
            "HLT_Mu0_Barrel_L1HP10_v",
            "HLT_Mu0_Barrel_L1HP11_v",
            "HLT_Mu9_Barrel_L1HP10_IP6_v",
            "HLT_Mu10_Barrel_L1HP11_IP6_v",

            "HLT_Mu3er1p5_PFJet100er2p5_PFMET90_PFMHT90_IDTight_v",
            "HLT_Mu3_L1SingleMu5orSingleMu7_v",
]

fired_HLTs = [
            "HLT_VBF_DiPFJet",
            "HLT_Ele",
            "HLT_BTagMu_AK",
            "HLT_HT3",
            "HLT_Diphoton",
            "HLT_AK8PFJet",
            "HLT_PFHT",
            "HLT_QuadPFJet",
            "HLT_DoubleMediumCharged"
]

import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing('python')

options.register('isMC', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Run this on real data"
)

options.register('maxE', -1,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.int,
    "Maximum number of events"
)

options.register('debug', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Debugging"
)
options.register('period', '2024I',
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Period of the data taking"
)
options.register('globalTag', 'NOTSET',
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Set global tag"
)

options.parseArguments()





process = cms.Process("Rootuple")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
#process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')

# Global tag and input file
GlobalTag_dict = {
    '2024G' : '140X_dataRun3_Prompt_v4',
    '2024I' : '140X_dataRun3_Prompt_v4',
}

data_file_dict = {
    '2023C' : '/store/data/Run2023C/ParkingDoubleMuonLowMass7/MINIAOD/PromptReco-v4/000/367/770/00000/0c62c10b-6629-4caf-9f6f-ed6c0bbc65b0.root',
    '2023D' : '/store/data/Run2023D/Muon1/MINIAOD/PromptReco-v2/000/370/776/00000/a92b94e8-1455-4a5d-b4c9-323e43d486f9.root',
    '2024B' : '/store/data/Run2024B/ParkingDoubleMuonLowMass0/MINIAOD/PromptReco-v1/000/379/058/00000/d57fe8ca-ccb0-4df9-a027-d6fa9788b51d.root',
    '2024E' : '/store/data/Run2024E/ParkingDoubleMuonLowMass0/MINIAOD/PromptReco-v1/000/380/963/00000/01db270e-3fc8-41c3-b92a-c7477c365533.root',
    '2024I' : '/store/data/Run2024I/ParkingDoubleMuonLowMass0/MINIAOD/PromptReco-v1/000/386/478/00000/18ef5008-85db-44f2-a127-be7946bb5221.root',
}
mc_file_dict = {
    '2022EE' : '',
    '2022preEE' : '',
}

#from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
from Configuration.AlCa.GlobalTag import GlobalTag
globalTag = options.globalTag if options._beenSet['globalTag'] else GlobalTag_dict[options.period]
process.GlobalTag = GlobalTag(process.GlobalTag, globalTag, '')
## Message Logger and Event range
process.MessageLogger.cerr.FwkReport.reportEvery = 10000 
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
process.options.allowUnscheduled = cms.untracked.bool(True)
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(options.maxE))

data_file = mc_file_dict[options.period] if options.isMC else data_file_dict[options.period]
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(data_file)
)

# process.triggerSelection = cms.EDFilter("TriggerResultsFilter",
#                                         triggerConditions = cms.vstring(#'HLT_Dimuon25_Jpsi_v*',
#                                                                         #'HLT_DoubleMu4_JpsiTrkTrk_Displaced_v*',
#                                                                         #'HLT_DoubleMu4_MuMuTrk_Displaced_v*',
#                                                                         #'HLT_DoubleMu4_JpsiTrk_Bc_v*',
#                                                                         #'HLT_DoubleMu4_LowMass_Displaced_v*',
#                                                                         'HLT_DoubleMu4_Jpsi_Displaced_v*'                                   
#                                                                        ),
#                                         hltResults = cms.InputTag( "TriggerResults", "", "HLT" ),
#                                         l1tResults = cms.InputTag( "" ),
#                                         throw = cms.bool(False)
#                                         )

#process.load("myAnalyzers.JPsiKsPAT.PsikaonRootupler_cfi")
#process.rootuple.dimuons = cms.InputTag('slimmedMuons')
process.rootuple = cms.EDAnalyzer('MuMu',
                          muons = cms.InputTag("slimmedMuons"),
                          Trak = cms.InputTag("packedPFCandidates"),
                          #Trak_lowpt = cms.InputTag("lostTracks"),
                          #GenParticles = cms.InputTag("genParticles"),
                          GenParticles = cms.InputTag("prunedGenParticles"),
                          packedGenParticles = cms.InputTag("packedGenParticles"),
                          
                          primaryVertices = cms.InputTag("offlineSlimmedPrimaryVertices"),
                          bslabel = cms.InputTag("offlineBeamSpot"),
                          
                          TriggerInput = cms.InputTag("slimmedPatTrigger"),
                          TriggerResults = cms.InputTag("TriggerResults", "", "HLT"),
                          algInputTag = cms.InputTag("gtStage2Digis", "", "RECO"),
                          l1Muons = cms.InputTag("gmtStage2Digis", "Muon", "RECO"),
                          HLTPaths = cms.vstring(HLT_Paths),
                          HLTPathsFired = cms.vstring(fired_HLTs),
                          L1Seeds = cms.vstring(L1_seeds),
                          OnlyBest = cms.bool(False),
                          isMC = cms.bool(options.isMC),
                          OnlyGen = cms.bool(False),
                          mumuMassConstraint = cms.bool(False),       
                          mumuMasscut     = cms.vdouble(0,15),                                  
                          Trkmass           = cms.double(0.493677),
                          #Trkmass           = cms.double(0.13957018),
                          BarebMasscut      = cms.vdouble(4.2,6.8),
                          bMasscut          = cms.vdouble(5.0,6.0),
                          debug = cms.bool(options.debug)        
                          )


dataset_name = options.period
file_name = f'Rootuple_DiMu-MiniAOD_{dataset_name}.root'
if options.isMC:
    file_name = f'Rootuple_MC_DiMu-MiniAOD_{dataset_name}.root'

    
process.TFileService = cms.Service("TFileService",
       #fileName = cms.string('Rootuple_Butomumu_2023-MiniAOD.root'),
       fileName = cms.string(file_name),
)

process.mySequence = cms.Sequence(
                                   #process.triggerSelection *
                                   process.rootuple
				   )

#process.p = cms.Path(process.mySequence)
#process.p = cms.Path(process.triggerSelection*process.rootuple)
process.p = cms.Path(process.rootuple)


