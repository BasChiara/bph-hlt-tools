import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetHistMinimumZero(True)

import array
import os
import sys

bph_ntuples = {
    "file" : "/eos/user/c/cbasile/HLT_DoubleMu/CMSSW_14_0_5/src/myAnalyzers/bph-hlt-tools/test/Rootuple_MC_DiMu-MiniAOD_2023preBPix.root",
    "tree" : "rootuple/ntuple",
    "selection" : ' && '.join([
        '(DiMu_mass>2.9) & (DiMu_mass<3.3)',
        "(DiMu_Prob > 0.005)",
        "(DiMu_mu1_pt>8) & (DiMu_mu2_pt>2)",
        "(mu1Global==1)",
        "(mu1loose==1)",
        "(mu2loose==1)",
        "(mu1_L1_match==1)",
        "(HLT_Mu8_v==1) & (mu1_HLT_Mu8_v ==1)",
    ]),
    "probesel" : '&'. join([
        #"(mu2_L1_match==1)",
        "(mu2_HLT_Mu0_L1DoubleMu_v == 1)",
    ])
}
pog_ntuples = {
    "file" : "/eos/user/c/cbasile/BPH_trigger/CMSSW_13_0_5_patch2/src/MuonAnalysis/MuonAnalyzer/test/output.root",
    "tree" : "muon/Events",
    "selection" : ' & '.join([
        "(pair_mass>2.9) & (pair_mass<3.3)",
        "(pair_svprob > 0.005)",
        "(tag_pt>8.0) & (probe_pt>2.0)",
        "(tag_isGlobal==1)",
        "(tag_isLoose==1)",
        "(probe_isLoose)",
        "(HLT_Mu8_v==1) & (tag_HLT_Mu8_v ==1)",
        "(tag_l1dr < 0.5)",
        "(probe_isDuplicated == 0)",
    ]),
    "probesel" : '&'. join([
        #"(l1dr<0.7)",
        "(probe_HLT_Mu0_L1DoubleMu_v == 1)",
    ])
}

file_bph = ROOT.TFile.Open(bph_ntuples["file"])
file_pog = ROOT.TFile.Open(pog_ntuples["file"])
tree_bph = file_bph.Get(bph_ntuples["tree"])
tree_pog = file_pog.Get(pog_ntuples["tree"])
if not tree_bph or not tree_pog:
    print("Error: tree not found")
    sys.exit(1)
else :
    print(f"Trees found:")
    print(f" [NO SELECTION]  t&p pairs :\n  BPH {tree_bph.GetEntries()} \t muonPOG {tree_pog.GetEntries()}")
    print(f" [TAG SELECTION] t&p pairs :\n  BPH {tree_bph.GetEntries(bph_ntuples['selection'])} \t muonPOG {tree_pog.GetEntries(pog_ntuples['selection'])}")

vars_to_plot = {
    'probe_pt' : {
        'title' : 'probe-#mu p_{T} [GeV]',
        'bins'  : [0,1,2,3,4,5,6,7,8,9,10,12,14,16,18,20,25,30,40,50],
        'range' : (0, 30),
        'bph_var': 'DiMu_mu2_pt',
        'pog_var': 'probe_pt'
    },
    'tag_pt': {
        'title': 'tag-#mu p_{T} [GeV]',
        'bins': [0,1,2,3,4,5,6,7,8,9,10,12,14,16,18,20,25,30,40,50],
        'range': (0, 30),
        'bph_var': 'DiMu_mu1_pt',
        'pog_var': 'tag_pt'
    },
    'probe_eta': {
        'title': 'probe-#mu #eta',
        'bins': [-2.4, -1.2, -0.9, 0.9, 1.2, 2.4],
        'range': (-2.5, 2.5),
        'bph_var': 'DiMu_mu2_eta',
        'pog_var': 'probe_eta'
    },
    'tag_eta': {
        'title': 'tag-#mu #eta',
        'bins':  [-2.4, -1.2, -0.9, 0.9, 1.2, 2.4],
        'range': (-2.5, 2.5),
        'bph_var': 'DiMu_mu1_eta',
        'pog_var': 'tag_eta'
    },
    'pair_mass': {
        'title': 'pair mass [GeV]',
        'bins': [2.90, 3.00, 3.02, 3.04, 3.06, 3.08, 3.1, 3.12, 3.14, 3.16, 3.18, 3.20, 3.30],
        'range': (2.9, 3.3),
        'bph_var': 'DiMu_mass',
        'pog_var': 'pair_mass'
    },
    'pair_svprob': {
        'title': 'SV prob',
        'bins': 20,
        'range': (0, 1),
        'bph_var': 'DiMu_Prob',
        'pog_var': 'pair_svprob'
    },
    'pair_pt': {
        'title': 'pair p_{T} [GeV]',
        'bins': 10,
        'range': (10, 50),
        'bph_var': 'DiMu_pt',
        'pog_var': 'pair_pt'
    },
    'pair_eta': {
        'title': '#eta(#mu_{1}#mu_{2})',
        'bins': [-2.4, -1.2, -0.9, 0.9, 1.2, 2.4],
        'range': (-2.5, 2.5),
        'bph_var': 'DiMu_eta',
        'pog_var': 'pair_eta'
    },
    'pair_dR': {
        'title': '#Delta R(#mu_{1}, #mu_{2})',
        'bins': 20,
        'range': (0, 1.0),
        'bph_var': 'DiMu_dR',
        'pog_var': 'pair_dR'
    },
    'passProbe_pair_pt' : {
        'title': 'pass probe-#mu p_{T} [GeV]',
        'bins': 10,
        'range': (10, 50),
        'bph_var': 'DiMu_pt',
        'pog_var': 'pair_pt',
        'pasProbe_sel': True,
    },
    'passProbe_probe_pt': {
        'title': 'pass probe-#mu p_{T} [GeV]',
        'bins': [0,1,2,3,4,5,6,7,8,9,10,12,14,16,18,20,25,30,40,50],
        'range': (0, 30),
        'bph_var': 'DiMu_mu2_pt',
        'pog_var': 'probe_pt',
        'pasProbe_sel': True,
    },
    'passProbe_eta': {
        'title': 'pass probe-#mu #eta',
        'bins': [-2.4, -1.2, -0.9, 0.9, 1.2, 2.4],
        'range': (-2.5, 2.5),
        'bph_var': 'DiMu_mu2_eta',
        'pog_var': 'probe_eta',
        'pasProbe_sel': True,
    },
    'passProbe_pair_dR': {
        'title': 'pass #Delta R(#mu_{1}, #mu_{2})',
        'bins': 20,
        'range': (0, 1.0),
        'bph_var': 'DiMu_dR',
        'pog_var': 'pair_dR',
        'pasProbe_sel': True,
    },
}

for var, opts in vars_to_plot.items():
    # if list of bines is provided, use it
    if isinstance(opts['bins'], list):
        bins = array.array('d', opts['bins'])
        h_bph = ROOT.TH1F(f'h_bph_{var}', "", len(bins)-1, bins)
        h_pog = ROOT.TH1F(f'h_pog_{var}', "", len(bins)-1, bins)
    else:
        h_bph = ROOT.TH1F(f'h_bph_{var}', "", opts['bins'], opts['range'][0], opts['range'][1])
        h_pog = ROOT.TH1F(f'h_pog_{var}', "", opts['bins'], opts['range'][0], opts['range'][1])

    tree_bph.Draw(f'{opts["bph_var"]} >> h_bph_{var}', bph_ntuples["selection"]+ (' & ' + bph_ntuples["probesel"] if opts.get("pasProbe_sel", False) else ""))
    tree_pog.Draw(f'{opts["pog_var"]} >> h_pog_{var}', pog_ntuples["selection"]+ (' & ' + pog_ntuples["probesel"] if opts.get("pasProbe_sel", False) else ""))

    # ratio plot
    h_bph.Sumw2()
    h_pog.Sumw2()
    h_ratio = h_bph.Clone(f'h_ratio_{var}')
    h_ratio.Divide(h_pog)
    h_ratio.SetLineColor(ROOT.kBlack)
    h_ratio.SetMarkerStyle(20)
    h_ratio.SetMarkerSize(0.8)
    h_ratio.SetMarkerColor(ROOT.kBlack)
    h_ratio.GetYaxis().SetTitle('BPH/POG')
    h_ratio.GetYaxis().SetRangeUser(0.5, 1.5)
    h_ratio.GetYaxis().SetNdivisions(505)
    h_ratio.GetYaxis().SetTitleSize(0.1)
    h_ratio.GetXaxis().SetTitle(opts['title'])
    h_ratio.GetXaxis().SetLabelSize(0.1)
    h_ratio.GetYaxis().SetLabelSize(0.1)
    h_ratio.GetYaxis().SetTitleSize(0.1)
    h_ratio.GetYaxis().SetTitleOffset(0.5)
    h_ratio.GetXaxis().SetTitleSize(0.1)
    h_ratio.GetXaxis().SetTitleOffset(0.8)



    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    legend.AddEntry(h_bph, "BPH", "l")
    legend.AddEntry(h_pog, "POG", "l")
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)


    ratio_h = 0.25
    lateral_m = 0.1
    bottom_m = 0.2
    between_m = 0.01
    top_m = 0.1
    c = ROOT.TCanvas(f'c_{var}', f'c_{var}', 800, 800)
    upper_pad = ROOT.TPad(f'upper_pad_{var}', f'upper_pad_{var}', 0, ratio_h, 1, 1)
    upper_pad.SetMargin(lateral_m, lateral_m, between_m, top_m)
    upper_pad.Draw()
    upper_pad.cd()
    h_bph.SetLineColor(ROOT.kRed)
    h_pog.SetLineColor(ROOT.kBlue)
    h_bph.SetLineWidth(2)
    h_pog.SetLineWidth(2)
    h_bph.GetXaxis().SetTitle(opts['title'])
    h_bph.GetYaxis().SetTitle(f'Entries')
    h_bph.SetMaximum(max(h_bph.GetMaximum(), h_pog.GetMaximum())*1.2)
    h_bph.Draw('hist')
    h_pog.Draw('hist same')
    legend.Draw()
    c.cd()
    lower_pad = ROOT.TPad(f'lower_pad_{var}', f'lower_pad_{var}', 0, 0, 1, ratio_h)
    lower_pad.SetMargin(lateral_m, lateral_m, bottom_m, between_m)
    lower_pad.Draw()
    lower_pad.cd()
    lower_pad.SetGridy()
    h_ratio.Draw('ep')
    c.cd()
    c.SaveAs(f'plots/{var}.png')
    c.SaveAs(f'plots/{var}.pdf')
    c.SaveAs(f'plots/{var}.root')

    upper_pad.Clear()
    lower_pad.Clear()
    c.Clear()
    legend.Clear()
