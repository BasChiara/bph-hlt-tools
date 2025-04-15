import ROOT
ROOT.ROOT.EnableImplicitMT()
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
import utils as utils

import argparse
argparser = argparse.ArgumentParser(description='Get scale factors')
argparser.add_argument('--data', 
                       help='root file with data samples',
                       )
argparser.add_argument('--mc',
                          help='root file with mc samples',
                        )
argparser.add_argument('--output',
                          help='output directory',
                        )
argparser.add_argument('--verbose', action='store_true',
                        help='verbose output',
                        )
argparser.add_argument('--probe_var',
                        default='DiMu_mu2_pt',
                        help='probe variable',
                        )
argparser.add_argument('--eta_region',
                        default='cms',
                        choices=['cms', 'barrel', 'overlap', 'endcap'],
                        help='eta region',
                        )
args = argparser.parse_args()


probe_var = args.probe_var

# load data
print(f'[i] loading data from {args.data}')
f_data = ROOT.TFile.Open(args.data)
for e in f_data.GetListOfKeys():

  if probe_var in e.GetName() and args.eta_region in e.GetName() and 'Hist' in e.GetName():
    data_hist_name = e.GetName()
    print(f'[i] found histogram: {data_hist_name}')
    break
eff_data = f_data.Get(data_hist_name)
eff_data.SetDirectory(0)
f_data.Close()
# load mc
print(f'[i] loading mc from {args.mc}')
f_mc = ROOT.TFile.Open(args.mc)
for e in f_mc.GetListOfKeys():
  if probe_var in e.GetName() and args.eta_region in e.GetName() and 'Hist' in e.GetName():
    mc_hist_name = e.GetName()
    print(f'[i] found histogram: {mc_hist_name}')
    break
eff_mc = f_mc.Get(mc_hist_name)
eff_mc.SetDirectory(0)
f_mc.Close()

# calculate scale factors
h_sf = eff_data.Clone('Hist')
h_sf.SetDirectory(0)
h_sf.Divide(eff_mc)
h_sf.SetTitle('Scale factors')

# plot efficiency and scale factors
eff_data = utils.style_efficiency(eff_data, 
                                  x_label= eff_data.GetXaxis().GetTitle(),
                                  color=ROOT.kBlack
                                  )
eff_mc = utils.style_efficiency(eff_mc,
                                x_label= eff_mc.GetXaxis().GetTitle(),
                                color=ROOT.kRed
                                )
h_sf = utils.style_efficiency(h_sf,
                                x_label= h_sf.GetXaxis().GetTitle(),
                                color=ROOT.kBlack
                                )
h_sf.GetYaxis().SetTitle('Data/MC')
h_sf.GetYaxis().SetRangeUser(0.8, 1.2)
h_sf.GetYaxis().SetTitleSize(0.1)
h_sf.GetYaxis().SetLabelSize(0.1)
h_sf.GetYaxis().SetTitleOffset(0.5)
h_sf.GetYaxis().SetNdivisions(505)
h_sf.GetXaxis().SetTitleSize(0.1)
h_sf.GetXaxis().SetLabelSize(0.1)

c = ROOT.TCanvas('c', 'c', 800, 800)
legend = ROOT.TLegend(0.5, 0.15, 0.9, 0.4)
legend.SetBorderSize(0)
legend.SetFillStyle(0)
legend.AddEntry(eff_data, 'Data', 'PE')
legend.AddEntry(eff_mc, 'MC', 'PE')
# upper pad
pad1 = ROOT.TPad('pad1', 'pad1', 0, 0.3, 1, 1)
pad1.SetBottomMargin(0.03)
pad1.SetGrid()
pad1.Draw()
pad1.cd()
eff_data.Draw('PE')
eff_mc.Draw('P same')
legend.Draw()
c.cd()
# lower pad
pad2 = ROOT.TPad('pad2', 'pad2', 0, 0, 1, 0.3)
pad2.SetTopMargin(0.03)
pad2.SetBottomMargin(0.3)
pad2.SetGrid()
pad2.Draw()
pad2.cd()
h_sf.Draw('PE')
c.cd()
c.SaveAs(args.output + '.png')
c.SaveAs(args.output + '.pdf')

# save scale factors
out_file = args.output + '.root' if not args.output.endswith('.root') else args.output
print(f'[i] saving scale factors to {args.output}')
f_out = ROOT.TFile.Open(out_file, 'recreate')
eff_data.Write()
eff_mc.Write()
h_sf.Write()
c.Write()
f_out.Close()

