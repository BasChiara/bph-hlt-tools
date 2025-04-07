import ROOT
ROOT.ROOT.EnableImplicitMT()
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
import json


infile = 'input/L1matching_DATA.json'
tag = 'DiMu_mu2_pt_DATA_L1match'
#infile = 'input/tag_pTthreshold.json'
#tag = 'pTthreshold'
with open(infile) as f:
    files = json.load(f)

h_eff = {}
for k,v in files.items():
    f = ROOT.TFile.Open(v['file'])
    if not f:
        print(f'File {v["file"]} not found')
        continue
    h_eff[k] = f.Get(v['name'])
    if not h_eff[k]:
        print(f'Hist {v["name"]} not found in file {v["file"]}')
        continue
    h_eff[k].SetDirectory(0)
    h_eff[k].SetLineColor(v['color'])
    h_eff[k].SetMarkerColor(v['color'])
    h_eff[k].SetMarkerStyle(20)
    h_eff[k].SetMarkerSize(0.8)
    f.Close()

c = ROOT.TCanvas('c', 'c', 800, 800)
leg = ROOT.TLegend(0.4, 0.15, 0.7, 0.4)
leg.SetBorderSize(0)
leg.SetFillStyle(0)
for i, (k,v) in enumerate(h_eff.items()):
    if i == 0:
        v.Draw('PE')
    else:
        v.Draw('PE same')
    leg.AddEntry(v, files[k]['legend'], 'lep')
leg.Draw()
out_name = f'efficiency_comparison_{tag}'
c.SetGrid()
c.SaveAs(f'{out_name}.png')
c.SaveAs(f'{out_name}.pdf')
c.SaveAs(f'{out_name}.root')