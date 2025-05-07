// -*- C++ -*-
//
// Package:    MuMu_demo
// Class:      MuMu_demo
// 

//=======================================
// Original author:  Chiara Basile      |
//         created:  April of 2025      |
//         <chiara.basile@cern.ch>      | 
//=======================================

// user include files
#include "myAnalyzers/bph-hlt-tools/src/MuMu_demo.h"

#include "FWCore/Common/interface/TriggerNames.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "TLorentzVector.h"
#include "TTree.h"
#include "TH2F.h"

#include "DataFormats/Common/interface/TriggerResults.h"
#include "FWCore/Common/interface/TriggerNames.h"

//
// constants, enums and typedefs
//
typedef math::Error<3>::type CovarianceMatrix;

//
// static data member definitions
//

//
// constructors and destructor
//

MuMu_demo::MuMu_demo(const edm::ParameterSet& iConfig)
  :
  matcher_(iConfig, consumesCollector()),
  ttrkToken_(esConsumes<TransientTrackBuilder, TransientTrackRecord>(edm::ESInputTag("", "TransientTrackBuilder"))),
  muon_Label(consumes<edm::View<pat::Muon>>(iConfig.getParameter<edm::InputTag>("muons"))),
  muonsViewToken_(consumes<edm::View<reco::Muon>>(iConfig.getParameter<edm::InputTag>("muons"))),
  trakCollection_label(consumes<edm::View<pat::PackedCandidate>>(iConfig.getParameter<edm::InputTag>("Trak"))),
  genCands_(consumes<reco::GenParticleCollection>(iConfig.getParameter < edm::InputTag > ("GenParticles"))), 
  packedGenToken_(consumes<pat::PackedGenParticleCollection>(iConfig.getParameter <edm::InputTag> ("packedGenParticles"))), 
  // L1 informations
  l1MatchesToken_(consumes<pat::TriggerObjectStandAloneMatch>(iConfig.getParameter<edm::InputTag>("l1Matches"))),
  l1MatchesQualityToken_(consumes<edm::ValueMap<int>>(iConfig.getParameter<edm::InputTag>("l1MatchesQuality"))),
  l1MatchesDeltaRToken_(consumes<edm::ValueMap<float>>(iConfig.getParameter<edm::InputTag>("l1MatchesDeltaR"))),
  propL1Token_(consumes<pat::TriggerObjectStandAloneCollection>(iConfig.getParameter<edm::InputTag>("propL1Muons"))),

  primaryVertices_Label(consumes<reco::VertexCollection>(iConfig.getParameter<edm::InputTag>("primaryVertices"))),
  BSLabel_(consumes<reco::BeamSpot>(iConfig.getParameter<edm::InputTag>("bslabel"))),
  // Trigger info and collection
  triggerCollection_(consumes<pat::TriggerObjectStandAloneCollection>(iConfig.getParameter<edm::InputTag>("TriggerInput"))),
  triggerResults_Label(consumes<edm::TriggerResults>(iConfig.getParameter<edm::InputTag>("TriggerResults"))),
  algTok_(consumes<BXVector<GlobalAlgBlk>>(iConfig.getParameter<edm::InputTag>("algInputTag"))),
  algInputTag_(consumes<GlobalAlgBlkBxCollection>(iConfig.getParameter<edm::InputTag>("algInputTag"))),
  l1MuonsToken_(consumes<BXVector<l1t::Muon>>(iConfig.getParameter<edm::InputTag>("l1Muons"))),
  HLTPaths_(iConfig.getParameter<std::vector<std::string>>("HLTPaths")),
  HLTPathsFired_(iConfig.getParameter<std::vector<std::string>>("HLTPathsFired")),
  L1Seeds_(iConfig.getParameter<std::vector<std::string>>("L1Seeds")),  
  gtUtil_( new l1t::L1TGlobalUtil( iConfig, consumesCollector(), *this, iConfig.getParameter<edm::InputTag>("algInputTag"), iConfig.getParameter<edm::InputTag>("algInputTag"), l1t::UseEventSetupIn::RunAndEvent  )),
  
  OnlyBest_(iConfig.getParameter<bool>("OnlyBest")),
  isMC_(iConfig.getParameter<bool>("isMC")),
  OnlyGen_(iConfig.getParameter<bool>("OnlyGen")),
  
  // selection
  muonTrkPt_min_(iConfig.getParameter<double>("muonTrkPt_min")),
  mumuMassConstraint_(iConfig.getParameter<bool>("mumuMassConstraint")),
  mumuMasscut_(iConfig.getParameter<std::vector<double> >("mumuMasscut")),
  Trkmass_(iConfig.getParameter<double>("Trkmass")),
  BarebMasscut_(iConfig.getParameter<std::vector<double> >("BarebMasscut")),
  bMasscut_(iConfig.getParameter<std::vector<double> >("bMasscut")),
     
  debug_(iConfig.getParameter<bool>("debug")),
  tree_(0), //tree_muons(0), tree_gen_muons(0), tree_L1muons(0), tree_L2muons(0), tree_L3muons(0),

  mu1_charge(0), mu2_charge(0),
  mu1_L1_match(0), mu2_L1_match(0),
  mu1_L2_match(0), mu2_L2_match(0),
  mu1_L3_match(0), mu2_L3_match(0),

  DiMu_mu1_index(0),DiMu_mu2_index(0),
  
  mu1_pt(0), mu1_eta(0), mu1_phi(0),
  mu2_pt(0), mu2_eta(0), mu2_phi(0),
  

  mu1C2(0), mu1NHits(0), mu1NPHits(0),
  mu2C2(0), mu2NHits(0), mu2NPHits(0),
  mu1dxy(0), mu2dxy(0), mu1dz(0), mu2dz(0),
  mu1dxy_beamspot(0), mu2dxy_beamspot(0), 
  mu1dxy_err(0), mu2dxy_err(0),
  muon_dca(0),

  
  L1mu_pt(0), L1mu_eta(0), L1mu_phi(0), L1mu_etaAtVtx(0), L1mu_phiAtVtx(0), L1mu_charge(0), L1mu_quality(0),
  // my L1 matching
  L1_muons_closest(0), L1_muons_matched(0),
  L2mu_pt(0), L2mu_eta(0), L2mu_phi(0),
  L3mu_pt(0), L3mu_eta(0), L3mu_phi(0),

  hltsVector(HLTPaths_.size()),
  l1sVector(L1Seeds_.size()),
  hltsVector_fired(HLTPathsFired_.size()),
  mu1_hltsVector(HLTPaths_.size()),
  mu2_hltsVector(HLTPaths_.size()),
  DiMu_L1_dR(0), mumuL2_dr(0), mumuL3_dr(0),
 
  mu1soft(0), mu2soft(0), mu1medium(0), mu2medium(0), mu1tight(0), mu2tight(0), 
  mu1PF(0), mu2PF(0), mu1loose(0), mu2loose(0),
  mu1Tracker(0), mu2Tracker(0), mu1Global(0), mu2Global(0),  
 
  // *******************************************************
 
  nMu(0),
  
  DiMu_dR(0),
  DiMu_mu1trk2_dR(0), DiMu_mu2trk1_dR(0),
  DiMu_dz(0),
  DiMu_mass(0), DiMu_mass_err(0), 
  DiMu_pt(0), DiMu_eta(0), DiMu_phi(0),
  DiMu_mu1_pt(0), DiMu_mu1_eta(0), DiMu_mu1_phi(0), 
  DiMu_mu2_pt(0), DiMu_mu2_eta(0), DiMu_mu2_phi(0), 

  L3_mu1_pt(0), L3_mu1_eta(0), L3_mu1_phi(0), 
  L3_mu2_pt(0), L3_mu2_eta(0), L3_mu2_phi(0), 

  // Primary Vertex (PV)
  nVtx(0),
  priVtxX(0), priVtxY(0), priVtxZ(0), priVtxXE(0), priVtxYE(0), priVtxZE(0), priVtxCL(0),
  priVtxXYE(0), priVtxXZE(0), priVtxYZE(0),
  
  // ************************ ****************************************************

  DiMu_chi2(0), DiMu_Prob(0), 
 
  DiMu_DecayVtxX(0),     DiMu_DecayVtxY(0),     DiMu_DecayVtxZ(0),
  DiMu_DecayVtxXE(0),    DiMu_DecayVtxYE(0),    DiMu_DecayVtxZE(0),
  DiMu_DecayVtxXYE(0),   DiMu_DecayVtxXZE(0),   DiMu_DecayVtxYZE(0),

  lxy(0), lxyerr(0), lxy_pv(0), lxy_pv_err(0), lxy_hlt(0), lxyerr_hlt(0),
  cosAlpha(0), cosAlpha_hlt(0),

  L1_mu1_dR(-1),
  L1_mu2_dR(-1),
  L1vtx_mu1_dR(-1),
  L1vtx_mu2_dR(-1),
  dR_muon1_L2(-1),
  dR_muon2_L2(-1),
  dR_muon1_L3(-1),
  dR_muon2_L3(-1),

  run(0), event(0),
  lumiblock(0),
  GENmu_pt(0), GENmu_eta(0), GENmu_phi(0),
  GENmu_charge(0), GENmu_status(0), GENmu_mother(0), GENmu_grandmother(0)
{
  //now do what ever initialization is needed
  initialize_variables();
}

//MuMu_demo::~MuMu_demo(){}


// ------------ method called to for each event  ------------
void MuMu_demo::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  //bool debug_ = true;
  if (debug_) std::cout << " - Welcome to the Analyzer " << std::endl;
  using std::vector;
  using namespace edm;
  using namespace reco;
  using namespace std;
  
  //*********************************
  // Get event content information
  //*********************************  

  // Generated particles
  edm::Handle<reco::GenParticleCollection> genParticles;
  iEvent.getByToken(genCands_, genParticles);
  if (isMC_) GenMuonMatching(iEvent, iSetup); 
 
  // Kinematic fit
  edm::ESHandle<TransientTrackBuilder> theB = iSetup.getHandle(ttrkToken_);

  edm::Handle< View<pat::PackedCandidate> > thePATTrackHandle;
  iEvent.getByToken(trakCollection_label,thePATTrackHandle);

  edm::Handle< View<pat::Muon> > thePATMuonHandle;
  iEvent.getByToken(muon_Label,thePATMuonHandle);
  
  edm::Handle<edm::View<reco::Muon>> muonsView;
  iEvent.getByToken(muonsViewToken_, muonsView);
  

  // L1 info
  edm::Handle<pat::TriggerObjectStandAloneMatch> l1Matches;
  iEvent.getByToken(l1MatchesToken_, l1Matches);
  edm::Handle<edm::ValueMap<int>> l1MatchesQuality;
  iEvent.getByToken(l1MatchesQualityToken_, l1MatchesQuality);
  edm::Handle<edm::ValueMap<float>> l1MatchesDeltaR;
  iEvent.getByToken(l1MatchesDeltaRToken_, l1MatchesDeltaR);
  edm::Handle<pat::TriggerObjectStandAloneCollection> propL1MuonsCollection;
  iEvent.getByToken(propL1Token_, propL1MuonsCollection);

  edm::Handle<std::vector<pat::TriggerObjectStandAlone>> triggerCollection;
  iEvent.getByToken(triggerCollection_, triggerCollection);

  
  // propagator
  matcher_.init(iSetup);


  reco::BeamSpot vertexBeamSpot;
  edm::Handle<reco::BeamSpot> beamSpot;
  iEvent.getByToken(BSLabel_, beamSpot);
  vertexBeamSpot = *beamSpot;

  
  lumiblock = iEvent.id().luminosityBlock();
  run       = iEvent.id().run();
  event     = iEvent.id().event();

  //*********************************
  //      GEN LEVEL INFORMATION     * 
  //*********************************
  gen_bc_p4.SetPtEtaPhiM(0.,0.,0.,0.);
  gen_jpsi_p4.SetPtEtaPhiM(0.,0.,0.,0.);
  gen_pion3_p4.SetPtEtaPhiM(0.,0.,0.,0.);
  gen_muon1_p4.SetPtEtaPhiM(0.,0.,0.,0.);
  gen_muon2_p4.SetPtEtaPhiM(0.,0.,0.,0.);
  gen_bc_vtx.SetXYZ(0.,0.,0.);
  gen_jpsi_vtx.SetXYZ(0.,0.,0.);
  gen_bc_ct = -9999.;
 
 
  //*********************************
  //        PRIMARY VERTEX          *
  //*********************************
  if(debug_) std::cout<< "---> Primary Vertex" << std::endl;

  reco::Vertex bestVtx;
  edm::Handle<reco::VertexCollection> primaryVertices_handle;
  iEvent.getByToken(primaryVertices_Label, primaryVertices_handle);

  // get primary vertex
  bestVtx = *(primaryVertices_handle->begin());

  priVtxX = bestVtx.x();
  priVtxY = bestVtx.y();
  priVtxZ = bestVtx.z();
  priVtxXE = bestVtx.covariance(0, 0);
  priVtxYE = bestVtx.covariance(1, 1);
  priVtxZE = bestVtx.covariance(2, 2);
  priVtxXYE = bestVtx.covariance(0, 1);
  priVtxXZE = bestVtx.covariance(0, 2);
  priVtxYZE = bestVtx.covariance(1, 2);

  priVtxCL = ChiSquaredProbability((double)(bestVtx.chi2()),(double)(bestVtx.ndof())); 
  nVtx = primaryVertices_handle->size();

  //*********************************
  //        TRIGGER INFORMATION      *
  //*********************************
  L1results(iEvent, iSetup);  
  HLTresults(iEvent);
  if(!TriggerCheck(hltsVector)){
    reset_variables();
    return;
  }
  edm::Handle<BXVector<l1t::Muon> > gmuons;
  iEvent.getByToken(l1MuonsToken_, gmuons);

  // loop over offline muon collection
  if (debug_){
    for (size_t i = 0; i < thePATMuonHandle->size(); i++) {

      // propagate the muon to the muon system
      edm::Ptr<pat::Muon> muon_trk(thePATMuonHandle, i);
      TrajectoryStateOnSurface propagated = matcher_.extrapolate(*muon_trk);
      float deltaR_prop_mu = -1;
      if (propagated.isValid()){
        GlobalPoint pos = propagated.globalPosition();
        deltaR_prop_mu = reco::deltaR(pos.eta(), pos.phi(), muon_trk->eta(), muon_trk->phi());
      }
      
      // access the association map to L1 muons by the pat::Muon key
      auto muRef = muonsView->refAt(i);
      edm::Ref<pat::TriggerObjectStandAloneCollection> matchRef = (*l1Matches)[muRef];
      // check to which L1 object the reco muon is matched
      if (debug_) std::cout << "offline mu " << i 
      << "\t pT = " << muRef->pt() 
      << "\t deltaR(offline, my-prop) = " << deltaR_prop_mu // dR between offline muon and propagated muon
      << std::endl;
      if (matchRef.isNonnull()){
        const pat::TriggerObjectStandAlone & matchedObj = *matchRef;
        if (debug_) std::cout << "[L1MuonMatcher] L1 mu \t pT = " << matchRef->pt() 
        << "\t quality = "           << (*l1MatchesQuality)[muRef]
        << "\t deltaR(L1, prop)  = " << (*l1MatchesDeltaR)[muRef] // dR between L1 muon and propagated muon
        << std::endl; 
      }
      // loop on propagated reco muons to L1 object they matched
      if (i >= propL1MuonsCollection->size()) continue;
      float deltaR_L1_prop = -1;
      const pat::TriggerObjectStandAlone& muon = propL1MuonsCollection->at(i);
      if (matchRef.isNonnull()){
        deltaR_L1_prop = reco::deltaR(matchRef->eta(), matchRef->phi(), muon.eta(), muon.phi());
      }
      if (debug_) std::cout << "[L1MuonMatcher] prop mu " << i 
      << "\t pT = " << muon.pt() 
      << "\t deltaR(offline, prop) = " << reco::deltaR(muRef->eta(), muRef->phi(), muon.eta(), muon.phi())
      << "\t deltaR(L1matched, prop) = " << deltaR_L1_prop
      << std::endl;

      // loop on L1 object
      for (auto it = gmuons->begin(0); it != gmuons->end(0); ++it){
        deltaR_prop_mu = -1.;
        if (propagated.isValid()) deltaR_prop_mu = reco::deltaR(propagated.globalPosition().eta(), propagated.globalPosition().phi(), it->eta(), it->phi() + 1.25 * M_PI/180.);
        if (debug_) std::cout << "L1 muon "
        << "\t pT = " << it->pt()
        << "\t deltaR(L1, offline) = " << reco::deltaR(muRef->eta(), muRef->phi(), it->eta(), it->phi())
        << "\t deltaR(L1vtx, offline) = " << reco::deltaR(muRef->eta(), muRef->phi(), it->etaAtVtx(), it->phiAtVtx())
        << "\t deltaR(L1, my-prop) = " << deltaR_prop_mu
        << std::endl;
      }

      std::cout << std::endl;
    }
  }
  bool USE_L1atVTX_ = false;
  //L1matching(iEvent, USE_L1atVTX_);
  L1matching_fix(iEvent, USE_L1atVTX_);

  //*********************************//
  //        J/psi --> mu+ mu-        //
  //*********************************//
  nMu = thePATMuonHandle->size();
  for (size_t index_mu1 = 0; index_mu1 < thePATMuonHandle->size(); ++index_mu1) {
    edm::Ptr<pat::Muon> iMuon1(thePATMuonHandle, index_mu1 );
    if (debug_) std::cout << " + muon1 pt = " << iMuon1->pt() << std::endl;
    
    //for (size_t index_mu2 = index_mu1+1; index_mu2 < thePATMuonHandle->size(); ++index_mu2) {
    for (size_t index_mu2 = 0; index_mu2 < thePATMuonHandle->size(); ++index_mu2) { //allow tag-probe exchange
      edm::Ptr<pat::Muon> iMuon2(thePATMuonHandle, index_mu2);
      
      if(iMuon1==iMuon2) continue;
      if(debug_) std::cout << " + muon2 pt = " << iMuon2->pt() << std::endl;

      //  ******* KINEMATIC VERTEX FIT ********
      DiMu_mu1_index = index_mu1;
      DiMu_mu2_index = index_mu2;
      //  muon tracks                  
      TrackRef glbTrack1 = iMuon1->track();
      TrackRef glbTrack2 = iMuon2->track();	  
      if( glbTrack1.isNull() || glbTrack2.isNull() ) continue;
      if((glbTrack1->pt()<muonTrkPt_min_) || glbTrack2->pt()<muonTrkPt_min_) continue;
      if(!(glbTrack2->quality(reco::TrackBase::highPurity)) || !(glbTrack1->quality(reco::TrackBase::highPurity))) continue;
      
      reco::TransientTrack muon1TT((*theB).build(glbTrack1));
      reco::TransientTrack muon2TT((*theB).build(glbTrack2));
      if(!buildMuMu(muon1TT, muon2TT, bestVtx, vertexBeamSpot)) continue;
      if (debug_) std::cout << " Dimuon pair mass = " << DiMu_mass << " +/- " << DiMu_mass_err << std::endl;

      // ********** TRIGGER MATCHING **********
      const pat::Muon* muon1 = &(*iMuon1);
      const pat::Muon* muon2 = &(*iMuon2);

      // propagate the muons to the muon system
      TrajectoryStateOnSurface propagated = matcher_.extrapolate(*muon1);
      mu1_isPropagated = propagated.isValid();
      if (propagated.isValid()){
        mu1_prop_pt = propagated.globalMomentum().perp(); 
        mu1_prop_eta  = propagated.globalPosition().eta(); mu1_prop_phi = propagated.globalPosition().phi();
      }
      propagated = matcher_.extrapolate(*muon2);
      mu2_isPropagated = propagated.isValid();
      if (propagated.isValid()){
        mu2_prop_pt = propagated.globalMomentum().perp(); 
        mu2_prop_eta  = propagated.globalPosition().eta(); mu2_prop_phi = propagated.globalPosition().phi();
      }     


      // L1 matching
      mu1_L1_idx = L1_muons_matched[index_mu1];
      mu1_L1_match = mu1_L1_idx >= 0;
      mu2_L1_idx = L1_muons_matched[index_mu2];
      mu2_L1_match = mu2_L1_idx >= 0;
      L1_mu1_dR = -1;
      L1_mu2_dR = -1;
      if (mu1_L1_idx >= 0) {
        auto L1mu  = gmuons->at(0, mu1_L1_idx);
        L1_mu1_pt  = L1mu.pt();
        L1_mu1_eta = L1mu.eta();
        L1_mu1_phi = L1mu.phi();
        L1_mu1_quality = L1mu.hwQual();
        L1_mu1_dR    = reco::deltaR(muon1->eta(), muon1->phi(), L1mu.eta(), L1mu.phi());
        L1vtx_mu1_dR = reco::deltaR(muon1->eta(), muon1->phi(), L1mu.etaAtVtx(), L1mu.phiAtVtx());
        if (mu1_isPropagated) mu1_L1prop_dR = reco::deltaR(mu1_prop_eta, mu1_prop_phi, L1mu.eta(), L1mu.phi());
      }
      if (mu2_L1_idx >= 0) {
        auto L1mu  = gmuons->at(0, mu2_L1_idx);
        L1_mu2_pt  = L1mu.pt();
        L1_mu2_eta = L1mu.eta();
        L1_mu2_phi = L1mu.phi();
        L1_mu2_quality = L1mu.hwQual();
        L1_mu2_dR    = reco::deltaR(muon2->eta(), muon2->phi(), L1mu.eta(),      L1mu.phi());
        L1vtx_mu2_dR = reco::deltaR(muon2->eta(), muon2->phi(), L1mu.etaAtVtx(), L1mu.phiAtVtx());
        if (mu2_isPropagated) mu2_L1prop_dR = reco::deltaR(mu2_prop_eta, mu2_prop_phi, L1mu.eta(), L1mu.phi());
      }
      if (mu1_L1_match==1 && mu2_L1_match==1){
        DiMu_L1_dR = reco::deltaR(L1_mu1_eta, L1_mu1_phi, L1_mu2_eta, L1_mu2_phi);
      }
      // L2 and L3 matching --> FIXME : I don't know if this is correct
      if (debug_) std::cout << " L2, L3  Matching " << std::endl;
      float dR2_muon1, dR2_muon2; 
      double dR2_threshold;
      dR2_threshold = 0.1 * 0.1;
      mu1_L2_match = 0;
      mu2_L2_match = 0;
      mu1_L3_match = 0;
      mu2_L3_match = 0;
      dR_muon1_L3 = -1;
      dR_muon2_L3 = -1;      

      pat::TriggerObjectStandAlone muon1_trgobj, muon2_trgobj;
      std::string hltMuColl_L2 = "hltL2MuonCandidates";
      std::string hltMuColl_L3 = "hltIterL3MuonCandidates";
      // L2 matching
      for (pat::TriggerObjectStandAlone obj : *triggerCollection) {
        if( obj.hasCollection(hltMuColl_L2) ) {
          dR2_muon1 = reco::deltaR2(iMuon1->eta(),iMuon1->phi(), obj.eta(), obj.phi());
          mu1_L2_match = (dR2_muon1 < dR2_threshold);
          dR2_muon2 = reco::deltaR2(iMuon2->eta(),iMuon2->phi(), obj.eta(), obj.phi());
          mu2_L2_match = (dR2_muon2 < dR2_threshold);
        }
      }// loop on trigger objects
      // L3 matching
      // .... muon 1 to L3
      dR2_threshold = 0.1 * 0.1;
      for (pat::TriggerObjectStandAlone obj : *triggerCollection) {      
        
        if( obj.hasCollection(hltMuColl_L3) ) {
          dR2_muon1 = reco::deltaR2(iMuon1->eta(),iMuon1->phi(), obj.eta(), obj.phi());                                
          if (dR2_muon1 < dR2_threshold) {
            dR2_threshold = dR2_muon1;
            mu1_L3_match = 1; 
            muon1_trgobj = obj;
            dR_muon1_L3 = sqrt(dR2_muon1);
          }          
        }
      }
      // .... muon 2 to L3
      dR2_threshold = 0.1 * 0.1; // FIXME : check this value
      for (pat::TriggerObjectStandAlone obj : *triggerCollection) {
        if( obj.hasCollection(hltMuColl_L3) ) {      
          dR2_muon2 = reco::deltaR2(iMuon2->eta(),iMuon2->phi(), obj.eta(), obj.phi());
          if ((dR2_muon2 < dR2_threshold) && (muon1_trgobj.pt()!=obj.pt())){
            dR2_threshold = dR2_muon2;
            mu2_L3_match=1;
            muon2_trgobj = obj;
            dR_muon2_L3 = sqrt(dR2_muon2);
          }
        }
      }
      if ( mu1_L3_match==1){
            L3_mu1_pt  = muon1_trgobj.pt();
            L3_mu1_eta = muon1_trgobj.eta();
            L3_mu1_phi = muon1_trgobj.phi();
        }
      
      if ( mu2_L3_match==1){
            L3_mu2_pt  = muon2_trgobj.pt();
            L3_mu2_eta = muon2_trgobj.eta();
            L3_mu2_phi = muon2_trgobj.phi();
      }  


      // HLT matching
      for (size_t i=0; i<HLTPaths_.size(); ++i) {
        if (muon1->triggered((HLTPaths_[i]+"*").c_str())) mu1_hltsVector[i] = 1;
        if (muon2->triggered((HLTPaths_[i]+"*").c_str())) mu2_hltsVector[i] = 1;
      }

      // GEN matching
      if (isMC_ && !OnlyGen_) {
        if (genMuons_match_idx[index_mu1] >= 0) {
          const reco::Candidate &gen = (*genParticles)[genMuons_match_idx[index_mu1]];
          mu1_gen_match = 1;
          mu1_gen_pt  = gen.pt();
          mu1_gen_eta = gen.eta();
          mu1_gen_phi = gen.phi();
          mu1_gen_dR  = reco::deltaR(iMuon1->eta(), iMuon1->phi(), mu1_gen_eta, mu1_gen_phi);
        }
        if (genMuons_match_idx[index_mu2] >= 0) {
          const reco::Candidate &gen = (*genParticles)[genMuons_match_idx[index_mu2]];
          mu2_gen_match = 1;
          mu2_gen_pt  = gen.pt();
          mu2_gen_eta = gen.eta();
          mu2_gen_phi = gen.phi();
          mu2_gen_dR  = reco::deltaR(iMuon2->eta(), iMuon2->phi(), mu2_gen_eta, mu2_gen_phi);
        }
        
      }
      
      if (debug_) std::cout << " Muons IDs and properties " << std::endl;
      // ************ Different muons Id, and other properties  ****************
      
      mu1_charge = iMuon1->charge() ;
      mu2_charge = iMuon2->charge() ; 

      mu1_pt = iMuon1->pt() ;
      mu2_pt = iMuon2->pt() ; 

      mu1_eta = iMuon1->eta() ;
      mu2_eta = iMuon2->eta() ; 

      mu1_phi = iMuon1->phi() ;
      mu2_phi = iMuon2->phi() ; 

      mu1soft    = iMuon1->isSoftMuon(bestVtx) ;
      mu2soft    = iMuon2->isSoftMuon(bestVtx) ;
      mu1medium  = iMuon1->isMediumMuon();
      mu2medium  = iMuon2->isMediumMuon();
      mu1tight   = iMuon1->isTightMuon(bestVtx) ;
      mu2tight   = iMuon2->isTightMuon(bestVtx) ;
      mu1PF = iMuon1->isPFMuon();
      mu2PF = iMuon2->isPFMuon();
      mu1Tracker = iMuon1->isTrackerMuon();
      mu2Tracker = iMuon2->isTrackerMuon();
      mu1Global = iMuon1->isGlobalMuon();
      mu2Global = iMuon2->isGlobalMuon();
      mu1loose = muon::isLooseMuon(*iMuon1);
      mu2loose = muon::isLooseMuon(*iMuon2);

      mu1C2 =  glbTrack1->normalizedChi2() ;
      mu1NHits =  glbTrack1->numberOfValidHits() ;
      mu1NPHits =  glbTrack1->hitPattern().numberOfValidPixelHits() ;	       
      mu2C2 =  glbTrack2->normalizedChi2() ;
      mu2NHits =  glbTrack2->numberOfValidHits() ;
      mu2NPHits =  glbTrack2->hitPattern().numberOfValidPixelHits() ;
      mu1dxy = glbTrack1->dxy(bestVtx.position()) ;// 
      mu2dxy = glbTrack2->dxy(bestVtx.position()) ;// 
      mu1dz = glbTrack1->dz(bestVtx.position()) ;
      mu2dz = glbTrack2->dz(bestVtx.position()) ;

      DiMu_dR = reco::deltaR(iMuon1->eta(),iMuon1->phi(), iMuon2->eta(), iMuon2->phi());
      if(iMuon2->innerTrack().isNonnull() && iMuon2->innerTrack().isAvailable()){
        DiMu_mu1trk2_dR = reco::deltaR(iMuon1->eta(),iMuon1->phi(), iMuon2->innerTrack()->eta(), iMuon2->innerTrack()->phi());
      }
      if(iMuon1->innerTrack().isNonnull() && iMuon1->innerTrack().isAvailable()){
        DiMu_mu2trk1_dR = reco::deltaR(iMuon2->eta(),iMuon2->phi(), iMuon1->innerTrack()->eta(), iMuon1->innerTrack()->phi());
      }
      DiMu_dz = iMuon2->vz() - iMuon1->vz();
      
      mu1dxy_beamspot = glbTrack1->dxy(vertexBeamSpot.position()) ;// 
      mu2dxy_beamspot = glbTrack2->dxy(vertexBeamSpot.position()) ;// 

      mu1dxy_err = glbTrack1->dxyError() ; 
      mu2dxy_err = glbTrack2->dxyError() ;

      //fill the tree
      if (tree_) tree_->Fill();
      else edm::LogError("MuMu_demo") << "tree_ pointer is null!";

      //muonParticles.clear();
      //vFitMCParticles.clear();

	    
	  } // muon 2 loop
  }// muon 1 loop


  if (debug_) std::cout << " ---> Trees Filled" << std::endl;
  reset_variables();
  if (debug_) std::cout << "\n\n" << std::endl;

}// analyze()


// save information about HLT
void MuMu_demo::L1results(const edm::Event& iEvent, const edm::EventSetup& iSetup){
  if(debug_) std::cout<< "---> L1results()" << std::endl;
  l1sVector.resize( L1Seeds_.size(), 0);
  
  // initialize the L1TGlobalUtil object for parsing the L1 trigger menu
  gtUtil_->retrieveL1(iEvent, iSetup, algInputTag_);
  const vector<pair<string, bool> > decisionsFinal = gtUtil_->decisionsFinal();
  const vector<pair<string, bool> > decisionsInitial = gtUtil_->decisionsInitial();
  const vector<pair<string, bool> > decisionsInterm = gtUtil_->decisionsInterm();
  const vector<pair<string, double> > prescales = gtUtil_->prescales();
  const vector<pair<string, vector<int> > > masks = gtUtil_->masks();
  const string gtTriggerMenuName    = gtUtil_->gtTriggerMenuName();
  const string gtTriggerMenuVersion = gtUtil_->gtTriggerMenuVersion();
  const string gtTriggerMenuComment = gtUtil_->gtTriggerMenuComment();

  if (debug_) {
    std::cout << "gtTriggerMenuName    = " << gtTriggerMenuName << std::endl;
    std::cout << "gtTriggerMenuVersion = " << gtTriggerMenuVersion << std::endl;
    std::cout << "gtTriggerMenuComment = " << gtTriggerMenuComment << std::endl;
  }

  for (size_t i_l1t = 0; i_l1t < decisionsFinal.size(); i_l1t++){
    string l1tName = (decisionsFinal.at(i_l1t)).first;
    
    if (debug_ && false){
      for(std::size_t i_input = 0; i_input < L1Seeds_.size(); ++i_input) {
        if (l1tName.find(L1Seeds_[i_input]) != std::string::npos){
          std::cout << "\t - Name = " << l1tName << std::endl;
          std::cout << "\t - - decisionsInitial = " << decisionsInitial.at(i_l1t).second << std::endl;
          std::cout << "\t - - decisionsInterm  = " << decisionsInterm.at(i_l1t).second << std::endl;
          std::cout << "\t - - decisionsFinal   = " << decisionsFinal.at(i_l1t).second << std::endl;
          std::cout << "\t - - prescales        = " << prescales.at(i_l1t).second << std::endl;
          std::cout << "\t - - masks  (size)    = " << masks.at(i_l1t).second.size() << std::endl;
        }
      }
    }
    if ((decisionsFinal.at(i_l1t)).second == 1) {
      for(std::size_t i = 0; i < L1Seeds_.size(); ++i) {
        if (l1tName.find(L1Seeds_[i]) != std::string::npos){ 
          l1sVector[i] = 1;
          if(debug_) std::cout << " fired L1 Seed: " << L1Seeds_[i] << std::endl;
        }
      }
    }
  }// loop on L1 seeds
}//L1results


void MuMu_demo::HLTresults(const edm::Event& iEvent){
  
  if(debug_) std::cout<< "---> HLTresults()" << std::endl;
  hltsVector.resize( HLTPaths_.size(), 0);
  mu1_hltsVector.resize( HLTPaths_.size(), 0);
  mu2_hltsVector.resize( HLTPaths_.size(), 0);
  hltsVector_fired.resize( HLTPathsFired_.size(), 0);

  // unpack trigger info
  edm::Handle<edm::TriggerResults> triggerBits;
  iEvent.getByToken(triggerResults_Label, triggerBits);
  const edm::TriggerNames &names = iEvent.triggerNames(*triggerBits);
  
  for (unsigned int i = 0; i  < triggerBits->size(); i++) {
    std::string iName = names.triggerName(i);
    if (triggerBits->accept(i)) {
      for(std::size_t i = 0; i < HLTPaths_.size(); ++i) {          
        if (iName.find(HLTPaths_[i]) != std::string::npos) {
          hltsVector[i] = 1;
          if(debug_) std::cout << " found HLT Path: " << HLTPaths_[i] << std::endl;
        }
      }
      for(std::size_t i = 0; i < HLTPathsFired_.size(); ++i) {      
        if (iName.find(HLTPathsFired_[i]) != std::string::npos) hltsVector_fired[i] = 1;
      }
    }
  }

}//HLTresults

bool  MuMu_demo::TriggerCheck(const std::vector<int>& trigger_bits){
  int sum = std::accumulate(trigger_bits.begin(), trigger_bits.end(), 0);
  return sum > 0;
}


void MuMu_demo::L1matching(const edm::Event& iEvent, const bool& L1atVtx){
  // FIXME: not optimal when there is a better gemetrical matching for a softer muon

  // offline muons
  edm::Handle<edm::View<pat::Muon>> offline_muons;
  iEvent.getByToken(muon_Label, offline_muons);
  // L1 muons
  edm::Handle<BXVector<l1t::Muon> > L1_muons;
  iEvent.getByToken(l1MuonsToken_, L1_muons);

  const double deltaPhi_offset = 1.25 * M_PI/180.; //FIXME: hardcoded value
  const double dR_max_L1matching = 1.0; //FIXME: hardcoded value
  L1_muons_closest.resize(offline_muons->size());
  
  for (size_t i = 0; i < offline_muons->size(); ++i){
    const pat::Muon& off_muon = offline_muons->at(i);
    int l1_idx = 0;
    std::vector<std::pair<int,double>> L1idx_dR;
    if (L1atVtx){
      // use L1 muon at vertex
      for (auto L1_mu_it = L1_muons->begin(0); L1_mu_it != L1_muons->end(0); ++L1_mu_it){
        double dR = reco::deltaR(off_muon.eta(), off_muon.phi(), L1_mu_it->etaAtVtx(), L1_mu_it->phiAtVtx());
        if (dR < dR_max_L1matching) L1idx_dR.push_back(std::make_pair(l1_idx, dR));
        l1_idx++;
      } // L1 muon loop
    } else {
      // propagate the muon to the muon system
      TrajectoryStateOnSurface prop_muon = matcher_.extrapolate(off_muon);
      if (!prop_muon.isValid()) continue;
    
      // loop on L1 muons
      for (auto L1_mu_it = L1_muons->begin(0); L1_mu_it != L1_muons->end(0); ++L1_mu_it){
        double dR = reco::deltaR(prop_muon.globalPosition().eta(), prop_muon.globalPosition().phi(), L1_mu_it->eta(), L1_mu_it->phi() + deltaPhi_offset);
        if (dR < dR_max_L1matching) L1idx_dR.push_back(std::make_pair(l1_idx, dR));
        l1_idx++;
      }
    }
    // sort L1 muons by dR
    std::sort(L1idx_dR.begin(), L1idx_dR.end(), [](const std::pair<int,double>& a, const std::pair<int,double>& b) { return a.second < b.second; });
    if (debug_){
      std::cout << "Muon " << i << " L1 muons: " << std::endl;
      for (const auto& L1 : L1idx_dR) std::cout << " - L1 muon " << L1.first << " dR = " << L1.second << std::endl;
    }
    L1_muons_closest[i] = L1idx_dR;

  }// loop on offline muons
  
  // match L1 and offline muons
  L1_muons_matched.resize(offline_muons->size(), -1);
  for (size_t i = 0; i<offline_muons->size(); ++i){
    for (size_t j = 0; j<L1_muons_closest[i].size(); ++j){
      
      if (L1_muons_closest[i][j].second > dR_max_L1matching) continue;
      if (std::find(L1_muons_matched.begin(), L1_muons_matched.end(), L1_muons_closest[i][j].first) != L1_muons_matched.end()) continue;
      
      L1_muons_matched[i] = L1_muons_closest[i][j].first;
      break;
    }
  }// loop on offline muons
  // print results
  if(debug_){
    for (size_t i = 0; i < offline_muons->size(); ++i){
      std::cout << "Offline muon " << i << " matched to L1 muon " << L1_muons_matched[i] << std::endl;
    }
  }

}// L1matching()


void MuMu_demo::L1matching_fix(const edm::Event& iEvent, const bool& L1atVtx){

  // offline muons
  edm::Handle<edm::View<pat::Muon>> offline_muons;
  iEvent.getByToken(muon_Label, offline_muons);
  // L1 muons
  edm::Handle<BXVector<l1t::Muon> > L1_muons;
  iEvent.getByToken(l1MuonsToken_, L1_muons);

  const double deltaPhi_offset = 1.25 * M_PI/180.; //FIXME: hardcoded value
  const double dR_max_L1matching = 1.0; //FIXME: hardcoded value
  offline_closest.resize(L1_muons->size());
  
  // loop on L1 muons
  int l1_idx = 0;
  for (auto L1_mu_it = L1_muons->begin(0); L1_mu_it != L1_muons->end(0); ++L1_mu_it){
    std::vector<std::pair<int,double>> muidx_dR;
    for (size_t i = 0; i < offline_muons->size(); ++i){
      const pat::Muon& off_muon = offline_muons->at(i);
      double dR = 1000.;
      if (L1atVtx){
        dR = reco::deltaR(off_muon.eta(), off_muon.phi(), L1_mu_it->etaAtVtx(), L1_mu_it->phiAtVtx());
      }else{
        // propagate the muon to the muon system
        TrajectoryStateOnSurface prop_muon = matcher_.extrapolate(off_muon);
        //if (!prop_muon.isValid()) continue;
        dR = ( prop_muon.isValid() ?  reco::deltaR(prop_muon.globalPosition().eta(), prop_muon.globalPosition().phi(), L1_mu_it->eta(), L1_mu_it->phi() + deltaPhi_offset) : 1000);
      }
      muidx_dR.push_back(std::make_pair(i, dR));
        
    }// loop on offline muons
    
    // sort offline muons by dR
    std::sort(muidx_dR.begin(), muidx_dR.end(), [](const std::pair<int,double>& a, const std::pair<int,double>& b) { return a.second < b.second; });

    if(debug_){
      std::cout << "L1 muon " << l1_idx << std::endl;
      for (const auto& mu : muidx_dR) std::cout << " - offline muon " << mu.first << " dR = " << mu.second << std::endl;
    }
    offline_closest[l1_idx] = muidx_dR;

    l1_idx++;
  }// loop on L1 muons

  offline_matched.resize(L1_muons->size(), -1); // [N_L1] - index of the matched offline muon
  L1_muons_matched.resize(offline_muons->size(), -1); // [N_offline] - index of the matched L1 muon for each offline muon
  for (size_t i = 0; i<L1_muons->size(); ++i){
    for (size_t j = 0; j<offline_closest[i].size(); ++j){
      if (debug_) std::cout << "L1 " << i << " closest muon " << offline_closest[i][j].first << " dR = " << offline_closest[i][j].second << std::endl;
      if (offline_closest[i][j].second > dR_max_L1matching) continue;
      // check if the offline muon is already matched
      if (std::find(offline_matched.begin(), offline_matched.end(), offline_closest[i][j].first) != offline_matched.end()) {
        if (debug_) std::cout << "Offline muon " << offline_closest[i][j].first << " already matched" << std::endl;
        continue;
      }
      L1_muons_matched[offline_closest[i][j].first] = i;
      offline_matched[i] = offline_closest[i][j].first;
      break;
    }// loop on offline muons
  }// loop on L1 muons
  // print results
  if(debug_){
    for (size_t i = 0; i < offline_muons->size(); ++i){
      std::cout << "Offline muon " << i << " matched to L1 muon " << L1_muons_matched[i] << std::endl;
    }
  }

}// L1matching_fix()

bool MuMu_demo::buildMuMu(const reco::TransientTrack& ttrack1, const reco::TransientTrack& ttrack2, reco::Vertex& vertex, reco::BeamSpot& vertexBeamSpot){
  
  // trajectory state -> calculate DCA for the 2 muons
  FreeTrajectoryState mu1State = ttrack1.impactPointTSCP().theState();
  FreeTrajectoryState mu2State = ttrack2.impactPointTSCP().theState();
  if( !ttrack1.impactPointTSCP().isValid() || !ttrack2.impactPointTSCP().isValid() ) return false;
  // DCA between tracks
  ClosestApproachInRPhi cApp;
  cApp.calculate(mu1State, mu2State);
  if( !cApp.status() ) return false;
  float dca = fabs( cApp.distance() );	  

  //  KinematicParticleFactory
  KinematicParticleFactoryFromTransientTrack pFactory;
  float init_chi = 0., init_ndf = 0.; // initial chi2 and ndf before kinematic fits
  vector<RefCountedKinematicParticle> muonParticles;
  try {
      muonParticles.push_back(pFactory.particle(ttrack1,MUON_MASS_,init_chi,init_ndf,MUON_SIGMA_));
      muonParticles.push_back(pFactory.particle(ttrack2,MUON_MASS_,init_chi,init_ndf,MUON_SIGMA_));
  }
  catch(...) { 
      std::cout<<" Exception caught ... continuing 1 "<<std::endl; 
      return false;
  }
  // - perform kinematic fit
  KinematicParticleVertexFitter fitter;   
  RefCountedKinematicTree psiVertexFitTree;
  try {
      psiVertexFitTree = fitter.fit(muonParticles); 
  }
  catch (...) { 
      std::cout<<" Exception caught ... continuing 2 "<<std::endl; 
      return false;
  }
  if (!psiVertexFitTree->isValid())  return false; 
  
  psiVertexFitTree->movePointerToTheTop();
  RefCountedKinematicParticle mumu_vFit_cand_noMC   = psiVertexFitTree->currentParticle();
  RefCountedKinematicVertex   mumu_vFit_vertex_noMC = psiVertexFitTree->currentDecayVertex();

  // quality cuts
  if(mumu_vFit_vertex_noMC->chiSquared() < 0 || mumu_vFit_vertex_noMC->chiSquared() > 50)  return false;
  if(mumu_vFit_cand_noMC->currentState().mass()<mumuMasscut_[0] || mumu_vFit_cand_noMC->currentState().mass()>mumuMasscut_[1]) return false;

  double J_Prob_tmp   = TMath::Prob(mumu_vFit_vertex_noMC->chiSquared(),(int)mumu_vFit_vertex_noMC->degreesOfFreedom());
  if(J_Prob_tmp<0.001) return false;

  // refit particles
  // - muon 1
  psiVertexFitTree->movePointerToTheFirstChild();
  RefCountedKinematicParticle mu1Cand = psiVertexFitTree->currentParticle();
  KinematicState mu1cand_state = mu1Cand->currentState();
  // - muon 2
  psiVertexFitTree->movePointerToTheNextChild();
  RefCountedKinematicParticle mu2Cand = psiVertexFitTree->currentParticle();
  KinematicState mu2cand_state = mu2Cand->currentState();

  // refit vertex
  GlobalPoint secondaryVertex(mumu_vFit_vertex_noMC->position().x(), mumu_vFit_vertex_noMC->position().y(), mumu_vFit_vertex_noMC->position().z());
  GlobalError verr = mumu_vFit_vertex_noMC->error();

  // - displacement from the beamspot
  GlobalPoint displacementFromBeamspot(-1 * ((vertexBeamSpot.x0() - secondaryVertex.x()) +
                                            (secondaryVertex.z() - vertexBeamSpot.z0()) * vertexBeamSpot.dxdz()),
                                      -1 * ((vertexBeamSpot.y0() - secondaryVertex.y()) +
                                            (secondaryVertex.z() - vertexBeamSpot.z0()) * vertexBeamSpot.dydz()),
                                      0);
  lxy = displacementFromBeamspot.perp();
  lxyerr = sqrt(verr.rerr(displacementFromBeamspot));
  
  // - angle between dimuon momentum and displacement
  math::XYZVector pperp( mumu_vFit_cand_noMC->currentState().globalMomentum().x(),  mumu_vFit_cand_noMC->currentState().globalMomentum().y(), 0.);
  reco::Vertex::Point vperp(displacementFromBeamspot.x(), displacementFromBeamspot.y(), 0.);
  cosAlpha = vperp.Dot(pperp) / (vperp.R() * pperp.R());


  // - displacement from the primary vertex
  float dx_lxy = (mumu_vFit_vertex_noMC->position().x() - vertex.x());
  float dy_lxy = (mumu_vFit_vertex_noMC->position().y() - vertex.y());      
  math::XYZVector vPS( dx_lxy, dy_lxy, 0);
  float lxy_xhat  = (dx_lxy*dx_lxy)/vPS.perp2() ;
  float lxy_xyhat  = (dx_lxy*dy_lxy)/vPS.perp2();
  float lxy_yhat = (dy_lxy*dy_lxy)/vPS.perp2();

  float sp_xx = mumu_vFit_vertex_noMC->error().cxx()+vertex.covariance(0,0);
  float sp_xy = mumu_vFit_vertex_noMC->error().cyx()+vertex.covariance(0,1);
  float sp_yy = mumu_vFit_vertex_noMC->error().cyy()+vertex.covariance(1,1);
  lxy_pv  = sqrt(vPS.perp2());
  lxy_pv_err = sqrt(lxy_xhat*sp_xx +2*lxy_xyhat*sp_xy + lxy_yhat*sp_yy);



  //   ---------- Fill the tree  ------------
  // - dimuon kinematics
  DiMu_mass     =  mumu_vFit_cand_noMC->currentState().mass() ;
  DiMu_mass_err = sqrt(mumu_vFit_cand_noMC->currentState().kinematicParametersError().matrix()(6,6));
      
  DiMu_pt  = mumu_vFit_cand_noMC->currentState().globalMomentum().perp() ;
  DiMu_eta = mumu_vFit_cand_noMC->currentState().globalMomentum().eta() ;
  DiMu_phi = mumu_vFit_cand_noMC->currentState().globalMomentum().phi() ;

  DiMu_mu1_pt  = mu1cand_state.globalMomentum().perp();
  DiMu_mu1_eta = mu1cand_state.globalMomentum().eta();
  DiMu_mu1_phi = mu1cand_state.globalMomentum().phi();

  DiMu_mu2_pt  = mu2cand_state.globalMomentum().perp();
  DiMu_mu2_eta = mu2cand_state.globalMomentum().eta();
  DiMu_mu2_phi = mu2cand_state.globalMomentum().phi();

  DiMu_chi2 = mumu_vFit_vertex_noMC->chiSquared();
  DiMu_Prob   = J_Prob_tmp;

  muon_dca  = abs( cApp.distance() );
  // - dimuon vertex
  DiMu_DecayVtxX    = mumu_vFit_vertex_noMC->position().x();    
  DiMu_DecayVtxY    = mumu_vFit_vertex_noMC->position().y();
  DiMu_DecayVtxZ    = mumu_vFit_vertex_noMC->position().z();
  DiMu_DecayVtxXE   = mumu_vFit_vertex_noMC->error().cxx();   
  DiMu_DecayVtxYE   = mumu_vFit_vertex_noMC->error().cyy();   
  DiMu_DecayVtxZE   = mumu_vFit_vertex_noMC->error().czz();
  DiMu_DecayVtxXYE  = mumu_vFit_vertex_noMC->error().cyx();
  DiMu_DecayVtxXZE  = mumu_vFit_vertex_noMC->error().czx();
  DiMu_DecayVtxYZE  = mumu_vFit_vertex_noMC->error().czy();

  muonParticles.clear();
  return true;
} // buildMuMu()

// ----------- GEN INFO ----------------
void MuMu_demo::GetGenInfo(const edm::Event& iEvent, const edm::EventSetup& iSetup){
  if(debug_) std::cout<< "---> GetGenInfo()" << std::endl;
  // get the gen particles
  edm::Handle<reco::GenParticleCollection> genParticles;
  iEvent.getByToken(genCands_, genParticles);
  if (!genParticles.isValid()) {
    std::cout << "Error! Can't get the gen particles" << std::endl;
    return;
  }
  gen_jpsi_p4.SetPxPyPzE(0.,0.,0.,0.);
  gen_muon1_p4.SetPxPyPzE(0.,0.,0.,0.);
  gen_muon2_p4.SetPxPyPzE(0.,0.,0.,0.);

  // look for Jpsi -> mu+ mu-
  for (size_t i = 0; i < genParticles->size(); ++i) {
    const reco::Candidate &gen = (*genParticles)[i];
    
    if (!(gen.status() == 2 && abs(gen.pdgId()) == Jpsi_PDGid_)) continue;
    for (size_t k=0; k<gen.numberOfDaughters(); k++) {
      const reco::Candidate* dau = gen.daughter(k);
      if (fabs(dau->pdgId()) == muon_PDGid_){
        genJpsi_idx.push_back(i);
        if (debug_) std::cout << "Gen Jpsi->MuMu " << dau->pdgId() << " " << dau->pt() << " " << dau->eta() << " " << dau->phi() << std::endl;
      }
    }
  }
}// GetGenInfo()

void MuMu_demo::GenMuonMatching(const edm::Event& iEvent, const edm::EventSetup& iSetup){
  if (debug_) std::cout<< "---> GenMuonMatching()" << std::endl;
  // get the gen particles
  edm::Handle<reco::GenParticleCollection> genParticles;
  iEvent.getByToken(genCands_, genParticles);
  if (!genParticles.isValid()) {
    std::cout << "Error! Can't get the gen particles" << std::endl;
    return;
  }
  // get the muons
  edm::Handle<edm::View<pat::Muon>> offline_muons;
  iEvent.getByToken(muon_Label, offline_muons);
  if (!offline_muons.isValid()) {
    std::cout << "Error! Can't get the muons" << std::endl;
    return;
  }
  genMuons_match_idx.resize(offline_muons->size(), -1);
  // loop on gen particles
  for (size_t i = 0; i < genParticles->size(); ++i) {
    const reco::Candidate &gen = (*genParticles)[i];

    if (!(gen.status() == 1 && abs(gen.pdgId()) == muon_PDGid_)) continue;
    
    if (debug_) std::cout << "Gen muon: " << gen.pdgId() << " " << gen.pt() << " " << gen.eta() << " " << gen.phi() << std::endl;
    // loop on offline muons
    for (size_t j = 0; j < offline_muons->size(); ++j) {
      const pat::Muon& off_muon = offline_muons->at(j);
      if (IsTheSame(gen, off_muon, 0.01)){
        genMuons_match_idx[j] =  i;
      }
    }
  }
  if (debug_) {
    for (size_t i = 0; i < offline_muons->size(); ++i) {
      std::cout << "Offline muon " << i << " matched to gen muon " << genMuons_match_idx[i] << std::endl;
    }
  }
}

bool MuMu_demo::IsTheSame(const pat::GenericParticle& tk, const pat::Muon& mu, const double& dR_MAX){
  bool same_dR = reco::deltaR(mu.eta(), mu.phi(), tk.eta(), tk.phi()) < dR_MAX;
  bool same_dpT = fabs(mu.pt() - tk.pt())/tk.pt() < 0.5;
  return same_dR && same_dpT;
  

  //return false;
}

bool MuMu_demo::isAncestor(const reco::Candidate* ancestor, const reco::Candidate * particle) {
    if (ancestor == particle ) return true;
    for (size_t i=0; i< particle->numberOfMothers(); i++) {
        if (isAncestor(ancestor,particle->mother(i))) return true;
    }
    return false;
}

double MuMu_demo::GetLifetime(TLorentzVector b_p4, TVector3 production_vtx, TVector3 decay_vtx) {
   TVector3 pv_dv = decay_vtx - production_vtx;
   TVector3 b_p3  = b_p4.Vect();
   pv_dv.SetZ(0.);
   b_p3.SetZ(0.);
   Double_t lxy   = pv_dv.Dot(b_p3)/b_p3.Mag();
   return lxy*b_p4.M()/b_p3.Mag();
}

// variable initialization
void MuMu_demo::initialize_variables(){
}// initialize()


void MuMu_demo::beginJob()
{

  std::cout << "Beginning analyzer job with value of isMC= " << isMC_ << std::endl;

  edm::Service<TFileService> fs;
  tree_          = fs->make<TTree>("ntuple",        "LowMass Dimuons ntuple");
  //tree_muons   = fs->make<TTree>("ntuple_muons",  "muons ntuple");
  //tree_L1muons = fs->make<TTree>("ntuple_L1muons","L1muons ntuple");
  //tree_L2muons = fs->make<TTree>("ntuple_L2muons","L2muons ntuple");
  //tree_L3muons = fs->make<TTree>("ntuple_L3muons","L3muons ntuple");


  tree_->Branch("run",      &run,       "run/I");
  tree_->Branch("event",    &event,     "event/L");
  tree_->Branch("lumiblock",&lumiblock,"lumiblock/I");
  tree_->Branch("nMu",&nMu,"nMu/i");
  tree_->Branch("DiMu_mass", &DiMu_mass);
  tree_->Branch("DiMu_pt" , &DiMu_pt);
  tree_->Branch("DiMu_eta", &DiMu_eta);
  tree_->Branch("DiMu_phi", &DiMu_phi);
  tree_->Branch("DiMu_dR", &DiMu_dR);
  tree_->Branch("DiMu_mu1trk2_dR", &DiMu_mu1trk2_dR);
  tree_->Branch("DiMu_mu2trk1_dR", &DiMu_mu2trk1_dR);
  tree_->Branch("DiMu_dz", &DiMu_dz);

  tree_->Branch("DiMu_mu1_index",  &DiMu_mu1_index);
  tree_->Branch("DiMu_mu2_index",  &DiMu_mu2_index);

  tree_->Branch("DiMu_mu1_pt",  &DiMu_mu1_pt);
  tree_->Branch("DiMu_mu1_eta", &DiMu_mu1_eta);
  tree_->Branch("DiMu_mu1_phi", &DiMu_mu1_phi);
  tree_->Branch("mu1_charge",   &mu1_charge);

  tree_->Branch("DiMu_mu2_pt",  &DiMu_mu2_pt);
  tree_->Branch("DiMu_mu2_eta", &DiMu_mu2_eta);
  tree_->Branch("DiMu_mu2_phi", &DiMu_mu2_phi);
  tree_->Branch("mu2_charge",   &mu2_charge);

  tree_->Branch("L1_mu1_pt",  &L1_mu1_pt);
  tree_->Branch("L1_mu1_eta", &L1_mu1_eta);
  tree_->Branch("L1_mu1_phi", &L1_mu1_phi);
  tree_->Branch("L1_mu1_quality", &L1_mu1_quality);
  
  tree_->Branch("L1_mu2_pt",  &L1_mu2_pt);
  tree_->Branch("L1_mu2_eta", &L1_mu2_eta);
  tree_->Branch("L1_mu2_phi", &L1_mu2_phi);
  tree_->Branch("L1_mu2_quality", &L1_mu2_quality);

  tree_->Branch("L3_mu1_pt",  &L3_mu1_pt);
  tree_->Branch("L3_mu1_eta", &L3_mu1_eta);
  tree_->Branch("L3_mu1_phi", &L3_mu1_phi);
  
  tree_->Branch("L3_mu2_pt",  &L3_mu2_pt);
  tree_->Branch("L3_mu2_eta", &L3_mu2_eta);
  tree_->Branch("L3_mu2_phi", &L3_mu2_phi);

  tree_->Branch("DiMu_chi2",    &DiMu_chi2);
  tree_->Branch("DiMu_Prob",  &DiMu_Prob);
       
  tree_->Branch("DiMu_DecayVtxX",     &DiMu_DecayVtxX);
  tree_->Branch("DiMu_DecayVtxY",     &DiMu_DecayVtxY);
  tree_->Branch("DiMu_DecayVtxZ",     &DiMu_DecayVtxZ);
  tree_->Branch("DiMu_DecayVtxXE",    &DiMu_DecayVtxXE);
  tree_->Branch("DiMu_DecayVtxYE",    &DiMu_DecayVtxYE);
  tree_->Branch("DiMu_DecayVtxZE",    &DiMu_DecayVtxZE);
  tree_->Branch("DiMu_DecayVtxXYE",   &DiMu_DecayVtxXYE);
  tree_->Branch("DiMu_DecayVtxXZE",   &DiMu_DecayVtxXZE);
  tree_->Branch("DiMu_DecayVtxYZE",   &DiMu_DecayVtxYZE);

  tree_->Branch("lxy", &lxy);
  tree_->Branch("lxyerr", &lxyerr);

  tree_->Branch("lxy_pv", &lxy_pv);
  tree_->Branch("lxy_pv_err", &lxy_pv_err);

  tree_->Branch("lxy_hlt", &lxy_hlt);
  tree_->Branch("lxyerr_hlt", &lxyerr_hlt);

  tree_->Branch("cosAlpha", &cosAlpha);
  tree_->Branch("cosAlpha_hlt", &cosAlpha_hlt);

  tree_->Branch("L1_mu1_dR", &L1_mu1_dR);
  tree_->Branch("L1_mu2_dR", &L1_mu2_dR);
  tree_->Branch("L1vtx_mu1_dR", &L1vtx_mu1_dR);
  tree_->Branch("L1vtx_mu2_dR", &L1vtx_mu2_dR);
  tree_->Branch("dR_muon1_L2", &dR_muon1_L2);
  tree_->Branch("dR_muon2_L2", &dR_muon2_L2);
  tree_->Branch("dR_muon1_L3", &dR_muon1_L3);
  tree_->Branch("dR_muon2_L3", &dR_muon2_L3);

  tree_->Branch("priVtxX",  &priVtxX, "priVtxX/D");
  tree_->Branch("priVtxY",  &priVtxY, "priVtxY/D");
  tree_->Branch("priVtxZ",  &priVtxZ, "priVtxZ/D");
  tree_->Branch("priVtxXE", &priVtxXE, "priVtxXE/D");
  tree_->Branch("priVtxYE", &priVtxYE, "priVtxYE/D");
  tree_->Branch("priVtxZE", &priVtxZE, "priVtxZE/D");
  tree_->Branch("priVtxXYE",&priVtxXYE, "priVtxXYE/D");
  tree_->Branch("priVtxXZE",&priVtxXZE, "priVtxXZE/D");
  tree_->Branch("priVtxYZE",&priVtxYZE, "priVtxYZE/D");
  tree_->Branch("priVtxCL", &priVtxCL, "priVtxCL/D");

  tree_->Branch("nVtx",       &nVtx);


  //tree_muons->Branch("run",      &run,       "run/I");
  //tree_muons->Branch("event",    &event,     "event/L");
  //tree_muons->Branch("lumiblock",&lumiblock,"lumiblock/I");

  //tree_L1muons->Branch("run",      &run,       "run/I");
  //tree_L1muons->Branch("event",    &event,     "event/L");
  //tree_L1muons->Branch("lumiblock",&lumiblock,"lumiblock/I");

  //tree_L2muons->Branch("run",      &run,       "run/I");
  //tree_L2muons->Branch("event",    &event,     "event/L");
  //tree_L2muons->Branch("lumiblock",&lumiblock,"lumiblock/I");

  //tree_L3muons->Branch("run",      &run,       "run/I");
  //tree_L3muons->Branch("event",    &event,     "event/L");
  //tree_L3muons->Branch("lumiblock",&lumiblock,"lumiblock/I");
    
  // *************************
  tree_->Branch("mu1C2",&mu1C2);  
  tree_->Branch("mu1NHits",&mu1NHits);
  tree_->Branch("mu1NPHits",&mu1NPHits);
  tree_->Branch("mu2C2",&mu2C2);  
  tree_->Branch("mu2NHits",&mu2NHits);
  tree_->Branch("mu2NPHits",&mu2NPHits);
  tree_->Branch("mu1dxy",&mu1dxy);
  tree_->Branch("mu2dxy",&mu2dxy);
  tree_->Branch("mu1dz",&mu1dz);
  tree_->Branch("mu2dz",&mu2dz);
  
  tree_->Branch("mu1dxy_beamspot",&mu1dxy_beamspot);
  tree_->Branch("mu2dxy_beamspot",&mu2dxy_beamspot);
  tree_->Branch("mu1dxy_err",&mu1dxy_err);
  tree_->Branch("mu2dxy_err",&mu2dxy_err);

  tree_->Branch("muon_dca",&muon_dca);

  tree_->Branch("mu1_L1_match", &mu1_L1_match);
  tree_->Branch("mu1_L1_idx", &mu1_L1_idx);
  tree_->Branch("mu1_isPropagated", &mu1_isPropagated);
  tree_->Branch("mu1_prop_pt", &mu1_prop_pt);
  tree_->Branch("mu1_prop_eta", &mu1_prop_eta);
  tree_->Branch("mu1_prop_phi", &mu1_prop_phi);
  tree_->Branch("mu1_L1prop_dR", &mu1_L1prop_dR);
  tree_->Branch("mu1_L2_match", &mu1_L2_match);
  tree_->Branch("mu1_L3_match", &mu1_L3_match);


  tree_->Branch("mu2_L1_match", &mu2_L1_match);
  tree_->Branch("mu2_L1_idx", &mu2_L1_idx);
  tree_->Branch("mu2_isPropagated", &mu2_isPropagated);
  tree_->Branch("mu2_prop_pt", &mu2_prop_pt);
  tree_->Branch("mu2_prop_eta", &mu2_prop_eta);
  tree_->Branch("mu2_prop_phi", &mu2_prop_phi);
  tree_->Branch("mu2_L1prop_dR", &mu2_L1prop_dR);
  tree_->Branch("mu2_L2_match", &mu2_L2_match);
  tree_->Branch("mu2_L3_match", &mu2_L3_match);

  tree_->Branch("DiMu_L1_dR",&DiMu_L1_dR);
  tree_->Branch("mumuL2_dr",&mumuL2_dr);
  tree_->Branch("mumuL3_dr",&mumuL3_dr);

  //tree_L1muons->Branch("L1mu_pt", &L1mu_pt); 
  //tree_L1muons->Branch("L1mu_eta", &L1mu_eta);
  //tree_L1muons->Branch("L1mu_phi", &L1mu_phi);
  //tree_L1muons->Branch("L1mu_etaAtVtx", &L1mu_etaAtVtx);
  //tree_L1muons->Branch("L1mu_phiAtVtx", &L1mu_phiAtVtx);
  //tree_L1muons->Branch("L1mu_charge", &L1mu_charge);
  //tree_L1muons->Branch("L1mu_quality", &L1mu_quality);

  tree_->Branch("mu1soft",&mu1soft);
  tree_->Branch("mu2soft",&mu2soft);
  tree_->Branch("mu1medium",&mu1medium);
  tree_->Branch("mu2medium",&mu2medium);
  tree_->Branch("mu1tight",&mu1tight);
  tree_->Branch("mu2tight",&mu2tight);
  tree_->Branch("mu1PF",&mu1PF);
  tree_->Branch("mu2PF",&mu2PF);
  tree_->Branch("mu1loose",&mu1loose);
  tree_->Branch("mu2loose",&mu2loose);
  tree_->Branch("mu1Tracker",&mu1Tracker);
  tree_->Branch("mu2Tracker",&mu2Tracker);
  tree_->Branch("mu1Global",&mu1Global);
  tree_->Branch("mu2Global",&mu2Global);

  // gen
  if (isMC_) { // FIXME : something not allocated
    tree_->Branch("mu1_gen_match", &mu1_gen_match);
    tree_->Branch("mu1_gen_pt",    &mu1_gen_pt);
    tree_->Branch("mu1_gen_eta",   &mu1_gen_eta);
    tree_->Branch("mu1_gen_phi",   &mu1_gen_phi);
    tree_->Branch("mu1_gen_dR",    &mu1_gen_dR);

    tree_->Branch("mu2_gen_match", &mu2_gen_match);
    tree_->Branch("mu2_gen_pt",    &mu2_gen_pt);
    tree_->Branch("mu2_gen_eta",   &mu2_gen_eta);
    tree_->Branch("mu2_gen_phi",   &mu2_gen_phi);
    tree_->Branch("mu2_gen_dR",    &mu2_gen_dR);
  }
  
  
  for(std::size_t i = 0; i < HLTPaths_.size(); ++i){ 
    tree_->Branch(HLTPaths_[i].c_str(), &hltsVector[i]);
    tree_->Branch(("mu1_"+HLTPaths_[i]).c_str(), &mu1_hltsVector[i]);
    tree_->Branch(("mu2_"+HLTPaths_[i]).c_str(), &mu2_hltsVector[i]);
  }

  for(std::size_t i = 0; i < HLTPathsFired_.size(); ++i){ 
    tree_->Branch(HLTPathsFired_[i].c_str(), &hltsVector_fired[i]);
  }
  for(std::size_t i = 0; i < L1Seeds_.size(); ++i){ 
    tree_->Branch(L1Seeds_[i].c_str(), &l1sVector[i]);
  } 

}// beginJob()

void MuMu_demo::reset_variables(){
  
  if (debug_) std::cout << " ---> reset_variables()" << std::endl;
  // --- muons --- 
  mu1_charge = 0, mu2_charge =0;
  mu1_gen_match = 0, mu2_gen_match = 0;

  nMu = 0;

  DiMu_dR = 0;
  DiMu_mu1trk2_dR = 0; DiMu_mu2trk1_dR = 0;
  DiMu_dz = -99; 
  DiMu_mass = 0; DiMu_mass_err = 0;
  DiMu_pt = 0;  DiMu_eta = 0;  DiMu_phi = 0;
  DiMu_mu1_pt = 0;  DiMu_mu1_eta = 0;  DiMu_mu1_phi = 0;
  DiMu_mu2_pt = 0;  DiMu_mu2_eta = 0;  DiMu_mu2_phi = 0;

  L3_mu1_pt = 0; L3_mu1_eta = 0; L3_mu1_phi = 0;
  L3_mu2_pt = 0; L3_mu2_eta = 0; L3_mu2_phi = 0;
  DiMu_L1_dR = -1.; mumuL2_dr = -1.; mumuL3_dr = -1.;

  DiMu_mu1_index = 0;  DiMu_mu2_index = 0;

  DiMu_chi2 = 0; 
  DiMu_Prob = 0;

  DiMu_DecayVtxX = 0;     DiMu_DecayVtxY = 0;     DiMu_DecayVtxZ = 0;
  DiMu_DecayVtxXE = 0;    DiMu_DecayVtxYE = 0;    DiMu_DecayVtxZE = 0;
  DiMu_DecayVtxXYE = 0;   DiMu_DecayVtxXZE = 0;   DiMu_DecayVtxYZE = 0;
  lxy = 0; lxyerr = 0;
  lxy_pv = 0; lxy_pv_err = 0;
  lxy_hlt = 0; lxyerr_hlt = 0;

  nVtx = 0;
  priVtxX = 0;     priVtxY = 0;     priVtxZ = 0; 
  priVtxXE = 0;    priVtxYE = 0;    priVtxZE = 0; priVtxCL = 0;
  priVtxXYE = 0;   priVtxXZE = 0;   priVtxYZE = 0;    

  mu1C2 = 0;
  mu1NHits = 0; mu1NPHits = 0;
  mu2C2 = 0;
  mu2NHits = 0; mu2NPHits = 0;
  mu1dxy = 0; mu2dxy = 0; mu1dz = 0; mu2dz = 0; 
  mu1dxy_beamspot = 0; mu2dxy_beamspot = 0;
  mu1dxy_err = 0; mu2dxy_err = 0;
  muon_dca = 0;

  mu1soft = 0; mu2soft = 0; mu1tight = 0; mu2tight = 0;
  mu1PF = 0; mu2PF = 0; mu1loose = 0; mu2loose = 0; 
  mu1Tracker = 0; mu2Tracker = 0; mu1Global = 0; mu2Global = 0;  


  mu1_L1_match = 0; mu1_L1_idx = -1;
  mu1_isPropagated = 0;
  mu1_prop_pt = -1; mu1_prop_eta = -99; mu1_prop_phi = -99; 
  mu1_L1prop_dR = -1;
  mu2_L1_match = 0; mu2_L1_idx = -1;
  mu2_isPropagated = 0;
  mu2_prop_pt = -1; mu2_prop_eta = -99; mu2_prop_phi = -99;
  mu2_L1prop_dR = -1;
  mu1_L2_match = 0;
  mu2_L2_match = 0;
  mu1_L3_match = 0;
  mu2_L3_match = 0;

  mu1_gen_match = 0; mu2_gen_match = 0;
  mu1_gen_pt =-99; mu1_gen_eta =-99; mu1_gen_phi =-99;
  mu2_gen_pt =-99; mu2_gen_eta =-99; mu2_gen_phi =-99;
  mu1_gen_dR = -1; mu2_gen_dR = -1;


  L1_mu1_dR = -1;
  L1_mu2_dR = -1;
  L1vtx_mu1_dR = -1;
  L1vtx_mu2_dR = -1;
  dR_muon1_L2 = -1;
  dR_muon2_L2 = -1;
  dR_muon1_L3 = -1;
  dR_muon2_L3 = -1;

  GENmu_pt.clear(); GENmu_eta.clear(); GENmu_phi.clear();

  L1_muons_matched.clear(); L1_muons_closest.clear();
  offline_matched.clear(); offline_closest.clear();
  L1mu_etaAtVtx.clear(); L1mu_phiAtVtx.clear();
  L1mu_quality.clear(); L1mu_charge.clear();

  genJpsi_idx.clear();
  genMuons_match_idx.clear();

  GENmu_charge.clear(); GENmu_status.clear(); 
  GENmu_mother.clear(); GENmu_grandmother.clear();

  l1sVector.clear();
  hltsVector_fired.clear();
  hltsVector.clear();
  mu1_hltsVector.clear();
  mu2_hltsVector.clear();
}// reset_variables()

// ------------ method called once each job just after ending the event loop  ------------
void MuMu_demo::endJob() {
  tree_->GetDirectory()->cd();
  tree_->Write();
}

//define this as a plug-in
DEFINE_FWK_MODULE(MuMu_demo);
