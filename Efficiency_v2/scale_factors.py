import ROOT
ROOT.ROOT.EnableImplicitMT()
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

import array as array
import json

import os
import utils as utils
import config as config
import cmsstyle

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
                        choices=['cms', 'barrel', 'overlap', 'endcap', 'all'],
                        help='eta region',
                        )
argparser.add_argument('--splitDR',
                        action='store_true',
                        help='split by deltaR between tag and probe muon',
                        )
argparser.add_argument('--trigger',
                        default='L1',
                        choices=['L1', 'HLT'],
                        help='trigger',
                        )
args = argparser.parse_args()


probe_var = args.probe_var
eta_region_list = [args.eta_region]
if eta_region_list[0] == 'all':
  eta_region_list = ['cms', 'barrel', 'overlap', 'endcap']
eta_plot_bins = array.array('d', [config.eta_bins[region][0] for region in eta_region_list] + [config.eta_bins[region][1] for region in eta_region_list])

deltaR_region_list = ['dRincl'] if not args.splitDR else config.deltaR_bins.keys()
deltaR_plot_bins = array.array('d', [config.deltaR_bins[region][0] for region in deltaR_region_list] + [config.deltaR_bins[region][1] for region in deltaR_region_list])

# summary json
summary_json = {}


for eta_region in eta_region_list:
  summary_json[eta_region] = {
     'eta_bin' : config.eta_bins[eta_region],
  }
  for deltaR_region in deltaR_region_list:
    
    print(f'\n --- {probe_var} in {eta_region} with {deltaR_region}')
    search_handle = f'{probe_var}_{eta_region}_{deltaR_region}'
   
    # --- INPUT ---
    # load data
    print(f'[i] loading data from {args.data}')
    eff_data = utils.get_hist_fromFile(args.data, handle = search_handle)
    if not eff_data:
        print(f'[E] error: {search_handle} not found in {args.data}')
        exit(1)
    # load mc
    print(f'[i] loading mc from {args.mc}')
    eff_mc = utils.get_hist_fromFile(args.mc, handle = search_handle)
    if not eff_mc:
        print(f'[E] error: {search_handle} not found in {args.mc}')
        exit(1)
    # --- OUTPUT ---
    if not os.path.exists(args.output):
        os.makedirs(args.output)
        print(f'[i] created output directory {args.output}')
    out_file_base = f'{args.output}/scale_factors_{args.trigger}_{search_handle}'

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
    h_sf = utils.style_scale_factor(h_sf,
                                    x_label= h_sf.GetXaxis().GetTitle(),
                                    color=ROOT.kBlack,
                                    marker=20,
                                    )
    x1_leg, x2_leg, y1_leg, y2_leg = 0.5, 0.9, 0.15, 0.4
    # legend
    legend = ROOT.TLegend(x1_leg, y1_leg, x2_leg, y2_leg)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.AddEntry(eff_data, 'Data', 'PE')
    legend.AddEntry(eff_mc, 'MC', 'PE')
    # text
    x_txt, y_txt = 0.15, 0.80
    text = ROOT.TLatex()
    text.SetTextSize(0.08)
    text.SetTextAlign(11)
    text.SetTextFont(42)


    c = ROOT.TCanvas('c', 'c', 800, 800)

    # upper pad
    pad1 = ROOT.TPad('pad1', 'pad1', 0, 0.3, 1, 1)
    pad1.SetBottomMargin(0.03)
    pad1.SetGrid()
    pad1.Draw()
    pad1.cd()
    eff_data.Draw('PE')
    eff_mc.Draw('P same')

    legend.Draw()
    text.DrawLatexNDC(x_txt, y_txt, f'{args.trigger}')
    text.SetTextSize(0.06)
    text.DrawLatexNDC(x_txt + 0.1, y_txt, f'{config.eta_bins[eta_region][0]} < |#eta| < {config.eta_bins[eta_region][1]}' + (f', {config.deltaR_bins[deltaR_region][0]} < #Delta R(#mu#mu) < {config.deltaR_bins[deltaR_region][1]}' if args.splitDR else ''))
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
    c.SaveAs(out_file_base + '.png')
    c.SaveAs(out_file_base + '.pdf')

    # save scale factors
    out_file = out_file_base + '.root'
    print(f'[i] saving scale factors to {args.output}')
    f_out = ROOT.TFile.Open(out_file, 'recreate')
    eff_data.Write()
    eff_mc.Write()
    h_sf.Write()
    c.Write()
    c.Close()

    # save summary json
    summary_json[eta_region][deltaR_region] = {
       'dR_bin' : config.deltaR_bins[deltaR_region],
    }
    summary_json[eta_region][deltaR_region][f'{probe_var}_bins'] = [eff_data.GetXaxis().GetBinLowEdge(i) for i in range(1, eff_data.GetNbinsX() + 2)]
    summary_json[eta_region][deltaR_region]['eff_MC'] = [eff_mc.GetBinContent(i) for i in range(1, eff_mc.GetNbinsX() + 1)]
    summary_json[eta_region][deltaR_region]['eff_MC_err'] = [eff_mc.GetBinError(i) for i in range(1, eff_mc.GetNbinsX() + 1)]
    summary_json[eta_region][deltaR_region]['eff_data'] = [eff_data.GetBinContent(i) for i in range(1, eff_data.GetNbinsX() + 1)]
    summary_json[eta_region][deltaR_region]['eff_data_err'] = [eff_data.GetBinError(i) for i in range(1, eff_data.GetNbinsX() + 1)]
    summary_json[eta_region][deltaR_region]['sf'] = [h_sf.GetBinContent(i) for i in range(1, h_sf.GetNbinsX() + 1)]
    summary_json[eta_region][deltaR_region]['sf_err'] = [h_sf.GetBinError(i) for i in range(1, h_sf.GetNbinsX() + 1)]

f_out.Close()

# save summary json
summary_json_file = os.path.join(args.output, f'efficiency_{args.trigger}_summary.json')
with open(summary_json_file, 'w') as f:
    json.dump(summary_json, f, indent=4)
print(f'[i] saved summary json to {summary_json_file}')
f.close()