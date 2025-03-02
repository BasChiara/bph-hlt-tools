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
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '124X_dataRun3_PromptAnalysis_v2') # for 2022


## Message Logger and Event range
process.MessageLogger.cerr.FwkReport.reportEvery = 10000 
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
process.options.allowUnscheduled = cms.untracked.bool(True)
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(options.maxE))

#data_file = '/store/data/Run2023C/ParkingDoubleMuonLowMass7/MINIAOD/PromptReco-v4/000/367/770/00000/0c62c10b-6629-4caf-9f6f-ed6c0bbc65b0.root'
#data_file = "/store/data/Run2023C/Muon0/MINIAOD/PromptReco-v4/000/367/770/00000/2c7a455b-304f-4ece-b66a-dabf30e9c7b1.root"
#data_file = "/store/data/Run2023D/Muon1/MINIAOD/PromptReco-v2/000/370/776/00000/a92b94e8-1455-4a5d-b4c9-323e43d486f9.root"
#data_file = "/store/data/Run2022F/Muon/MINIAOD/PromptReco-v1/000/360/389/00000/ad0997b9-ff20-4b2c-9c51-1d6ef49100f4.root"
#data_file = "/store/data/Run2022F/Muon/MINIAOD/PromptReco-v1/000/360/335/00000/db3a7d95-2b78-4e72-86e4-8436005406bf.root"
#data_file  = "/store/data/Run2022F/Muon/MINIAOD/PromptReco-v1/000/360/390/00000/be5c66b6-fea2-48f4-879f-846f6de0e511.root"
data_file   = "/store/data/Run2023C/Muon0/MINIAOD/PromptReco-v2/000/367/516/00000/042f54de-04d7-4823-bd01-1926572db8fe.root"
if options.isMC:
    data_file = "/store/mc/Run3Summer23MiniAODv4/Jpsito2Mu_JpsiPT8_TuneCP5_13p6TeV_pythia8/MINIAODSIM/MUO_POG_130X_mcRun3_2023_realistic_v14-v2/2520000/0c863e61-da9e-4b99-8a7b-2c0c6a3bc454.root"


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
                        mumuMasscut        = cms.vdouble(1.0, 5.0),                                  
                        Trkmass            = cms.double(0.493677),
                        BarebMasscut       = cms.vdouble(4.2,6.8),
                        bMasscut           = cms.vdouble(5.0,6.0),
                        
                        debug = cms.bool(options.debug)        
)

dataset_name = data_file.split('/')[4][:11]
dataset_name = ''
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


