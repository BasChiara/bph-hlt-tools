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
            "HLT_Mu8_v", 
            "HLT_Mu4_L1DoubleMu_v",
            "HLT_Mu0_L1DoubleMu_v",
]

fired_HLTs = [
            #"HLT_VBF_DiPFJet",
            #"HLT_Ele",
            #"HLT_BTagMu_AK",
            #"HLT_HT3",
            #"HLT_Diphoton",
            #"HLT_AK8PFJet",
            #"HLT_PFHT",
            #"HLT_QuadPFJet",
            #"HLT_DoubleMediumCharged"
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
options.register('debug', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Debugging"
)
options.parseArguments()





process = cms.Process("Rootuple")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
# Global tag and input file
GlobalTag_dict = {
    '2022preEE'   : '130X_mcRun3_2022_realistic_v5',
    '2023preBPix' : '130X_mcRun3_2023_realistic_v14',
    '2023BPix'    : '130X_mcRun3_2023_realistic_postBPix_v2',
    '2024G'       : '140X_dataRun3_Prompt_v4',
    '2024I'       : '140X_dataRun3_Prompt_v4',
}

data_file_dict = {
    'default': '',
    '2023C' : '/store/data/Run2023C/ParkingDoubleMuonLowMass7/MINIAOD/PromptReco-v4/000/367/770/00000/0c62c10b-6629-4caf-9f6f-ed6c0bbc65b0.root',
    '2023D' : '/store/data/Run2023D/Muon1/MINIAOD/PromptReco-v2/000/370/776/00000/a92b94e8-1455-4a5d-b4c9-323e43d486f9.root',
    '2024B' : '/store/data/Run2024B/ParkingDoubleMuonLowMass0/MINIAOD/PromptReco-v1/000/379/058/00000/d57fe8ca-ccb0-4df9-a027-d6fa9788b51d.root',
    '2024E' : '/store/data/Run2024E/ParkingDoubleMuonLowMass0/MINIAOD/PromptReco-v1/000/380/963/00000/01db270e-3fc8-41c3-b92a-c7477c365533.root',
    '2024I' : '/store/data/Run2024I/ParkingDoubleMuonLowMass0/MINIAOD/PromptReco-v1/000/386/478/00000/18ef5008-85db-44f2-a127-be7946bb5221.root',
}
mc_file_dict = {
    'default': '',
    '2022EE' : '',
    '2022preEE' : '/store/mc/Run3Summer22MiniAODv4/InclusiveDileptonMinBias_TuneCP5Plus_13p6TeV_pythia8/MINIAODSIM/validDigi_130X_mcRun3_2022_realistic_v5-v4/2820000/37b0bc85-0086-469f-aee3-7ed5506d86b1.root',
    '2023preBPix' :[ 
        '/store/mc/Run3Summer23MiniAODv4/Jpsito2Mu_JpsiPT8_TuneCP5_13p6TeV_pythia8/MINIAODSIM/MUO_POG_130X_mcRun3_2023_realistic_v14-v2/2520000/0c863e61-da9e-4b99-8a7b-2c0c6a3bc454.root',
        #'/store/mc/Run3Summer23MiniAODv4/Jpsito2Mu_JpsiPT8_TuneCP5_13p6TeV_pythia8/MINIAODSIM/MUO_POG_130X_mcRun3_2023_realistic_v14-v2/2520000/0ced0770-fbf6-4221-81ef-8c85715268a4.root'
        ],
    '2023BPix'  : '/store/mc/Run3Summer23MiniAODv4/Jpsito2Mu_JpsiPT8_TuneCP5_13p6TeV_pythia8/MINIAODSIM/MUO_POG_130X_mcRun3_2023_realistic_v14-v2/2520000/0c863e61-da9e-4b99-8a7b-2c0c6a3bc454.root',
}


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

# L1 Muon Matcher
import FWCore.ParameterSet.Config as cms

from TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAny_cfi import *
from TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAlong_cfi import *
from TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorOpposite_cfi import *
from RecoMuon.DetLayers.muonDetLayerGeometry_cfi import *
from math import pi

    # Choice of matching algorithm


muonL1MatcherParameters = cms.PSet(
    # Choice of matching algorithm
    useTrack = cms.string("tracker"),    # 'none' to use Candidate P4; or 'tracker', 'muon', 'global'
    useState = cms.string("atVertex"),   # 'innermost' and 'outermost' require the TrackExtra
    useSimpleGeometry = cms.bool(True),  # just use a cylinder plus two disks.
    fallbackToME1 = cms.bool(False),     # If propagation to ME2 fails, propagate to ME1

    useMB2InOverlap =  cms.bool(True),  # propagate to MB2 in overlap region (according to L1 experts OMTF uses MB2 as RF in all its coverage) 
    useStage2L1 = cms.bool(True),       # Use stage2 L1 instead of legacy one
    useStation2 = cms.bool(True),       # Use station 2 instead of station 1
    sortBy = cms.string("pt"),          # among compatible candidates, pick the highest pt one

    cosmicPropagationHypothesis = cms.bool(False),
    propagatorAlong = cms.ESInputTag("", "SteppingHelixPropagatorAlong"),
    propagatorAny = cms.ESInputTag("", "SteppingHelixPropagatorAny"),
    propagatorOpposite = cms.ESInputTag("", "SteppingHelixPropagatorOpposite"),
    
    # Matching Criteria
    maxDeltaR   = cms.double(1.0),
    maxDeltaPhi = cms.double(6),
    maxDeltaEta = cms.double(99),
    l1PhiOffset = cms.double(1.25 * pi/180.), ## Offset to add to L1 phi before matching (according to L1 experts)
)
### For L1 Singlets you 

process.muonL1Match = cms.EDProducer("L1MuonMatcher",
    muonL1MatcherParameters,

    # Reconstructed muons
    src = cms.InputTag("slimmedMuons"),

    # L1 Muon collection, and preselection on that collection
    matched      = cms.InputTag("gmtStage2Digis:Muon:"),
    preselection = cms.string("1"),

    # Fake filter labels for output
    setL1Label = cms.string("l1"),
    setPropLabel = cms.string("propagated"),

    # Write extra ValueMaps
    writeExtraInfo = cms.bool(True),

    # Min and Max BXs from l1t::BxVector (applies to stage 2 only)
    firstBX = cms.int32(0),
    lastBX  = cms.int32(0),
)

diMuonL1MatcherParameters = cms.PSet(
    propagatorAlong = cms.ESInputTag("", "SteppingHelixPropagatorAlong"),
    propagatorAny = cms.ESInputTag("", "SteppingHelixPropagatorAny"),
    propagatorOpposite = cms.ESInputTag("", "SteppingHelixPropagatorOpposite"),

    useSimpleGeometry = cms.bool(True),
    useStation2 = cms.bool(True),
    fallbackToME1 = cms.bool(False),
    
    cosmicPropagationHypothesis = cms.bool(False),
    useMB2InOverlap =  cms.bool(True),

    useTrack = cms.string("tracker"),    # 'none' to use Candidate P4; or 'tracker', 'muon', 'global'
    useState = cms.string("atVertex"),   # 'innermost' and 'outermost' require the TrackExtra 

    # Matching Criteria
    maxDeltaR   = cms.double(1.0),
    maxDeltaPhi = cms.double(6),
    maxDeltaEta = cms.double(99),
    l1PhiOffset = cms.double(1.25 * pi/180.), ## Offset to add to L1 phi before matching (according to L1 experts)
)
process.rootuple = cms.EDAnalyzer('MuMu_demo',
                        diMuonL1MatcherParameters,
                        # General input tags
                        muons = cms.InputTag("slimmedMuons"),
                        Trak = cms.InputTag("packedPFCandidates"),
                        GenParticles = cms.InputTag("prunedGenParticles"),
                        packedGenParticles = cms.InputTag("packedGenParticles"),
                        # L1 information
                        l1Matches        = cms.InputTag("muonL1Match"),
                        l1MatchesQuality = cms.InputTag("muonL1Match", "quality"),
                        l1MatchesDeltaR  = cms.InputTag("muonL1Match", "deltaR"),
                        propL1Muons      = cms.InputTag("muonL1Match", "propagatedReco"),               

                        
                        primaryVertices = cms.InputTag("offlineSlimmedPrimaryVertices"),
                        bslabel = cms.InputTag("offlineBeamSpot"),
                        # Trigger info and collection
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
                        
                        # selection
                        muonTrkPt_min     = cms.double(1.5),
                        mumuMassConstraint = cms.bool(False),       
                        mumuMasscut        = cms.vdouble(-1.0, 1e3), #1.0, 5.0                                 
                        Trkmass            = cms.double(0.493677),
                        BarebMasscut       = cms.vdouble(-1, 1e3), #4.2,6.8
                        bMasscut           = cms.vdouble(-1, 1e3), #5.0,6.0
                        
                        debug = cms.bool(options.debug)        
)

dataset_name = options.period
file_name = f'Rootuple_DiMu-MiniAOD_{dataset_name}.root'
if options.isMC:
    file_name = f'Rootuple_MC_DiMu-MiniAOD_{dataset_name}.root'

    
process.TFileService = cms.Service("TFileService",
    fileName = cms.string(file_name),
)

process.mySequence = cms.Sequence(
    process.muonL1Match +
    process.rootuple
)


process.p = cms.Path(
    process.muonL1Match +
    process.rootuple
)


