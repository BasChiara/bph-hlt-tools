import ROOT
ROOT.ROOT.EnableImplicitMT()
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
import argparse
import json
import glob
from array import array
import os
import sys

import config as config
import utils as utils

argparser = argparse.ArgumentParser(description='Cut and count efficiency')
argparser.add_argument('--data', 
                        help='json file with data samples',
                       )
argparser.add_argument('--selection',
                        help='json file with selection',
                        )
argparser.add_argument('--output',
                        help='output directory',
                        )
argparser.add_argument('--verbose', action='store_true',
                        help='verbose output',
                        )
args = argparser.parse_args()

# load data
print(f'[i] loading data from {args.data}')
try:
    with open(args.data) as f:
        data_info = json.load(f)
    f.close()
except:
    if os.path.exists(args.data):
        print(f'Error: {args.data} is not a valid json file')
    else:
        print(f'Error: {args.data} does not exist')
# load selection for tag and probe
tag_selection_, probe_selection_, sel_name = utils.selection_from_json(args.selection)
print(f'[T] tag selection: {tag_selection_}')
print(f'[P] probe selection: {probe_selection_}')

data_tag = '_'.join([
    data_info['process'],
    data_info['run_era'],
    data_info['tag'],
    sel_name,
])

# setup the output directory
if not os.path.exists(args.output):
    os.makedirs(args.output)
    print(f'[i] output directory created: {args.output}')
out_file_name = os.path.join(args.output, f'debug_{data_tag}.root')
print(f'[i] output file: {out_file_name}')

# check how many files are in the directory
data_files = []
for dataset in data_info['dataset']:
    print(f' - dataset : {dataset}')
    file_list = glob.glob(data_info['dataset'][dataset])
    print(f'   #file(s) = {len(file_list)}')
    data_files.extend(file_list)

# root dataframe for data
eta_selection = f"(DiMu_mu2_aeta > {config.eta_overlap[0]} && DiMu_mu2_aeta < {config.eta_overlap[1]})"
#eta_selection = f"(DiMu_mu2_aeta > {config.eta_barrel[0]} && DiMu_mu2_aeta < {config.eta_barrel[1]})"

data_tag = ROOT.RDataFrame(data_info["tree"], data_files).Define('DiMu_mu2_aeta', 'fabs(DiMu_mu2_eta)').Filter(tag_selection_).Filter(eta_selection)
print(f'[i] #events after TAG selection: {data_tag.Count().GetValue()}')


probe_var = "DiMu_mu2_pt"
threshold = 10
bins_probe = array('d', config.Bins1d[probe_var])
vars = ["DiMu_dR", "DiMu_mu1_eta", "L1_mu1_dR", "L1_mu2_dR", "L1vtx_mu1_dR", "L1vtx_mu2_dR",]
root_file = ROOT.TFile(out_file_name, 'RECREATE')
for v in vars:
    
    probe_selection = f"{probe_selection_} & {eta_selection}"
    print(f"[i] probe selection: {probe_selection}")
    
    bins = array('d', config.Bins1d[v])
    # pass below threshold
    h_pass_below = data_tag.Filter(probe_selection + f"&({probe_var} < {threshold})").Histo1D((f"pass_below{threshold}_{v}", f"pass_below{threshold}_{v}", len(bins)-1, bins), v)
    h_pass_below.SetDirectory(0)
    # fail below threshold
    h_fail_below = data_tag.Filter(f"!({probe_selection})&({probe_var} < {threshold})").Histo1D((f"fail_below{threshold}_{v}", f"fail_below{threshold}_{v}", len(bins)-1, bins), v)
    h_fail_below.SetDirectory(0)

    #pass above threshold
    h_pass_above = data_tag.Filter(probe_selection + f"& ({probe_var} > {threshold})").Histo1D((f"pass_above{threshold}_{v}", f"pass_above{threshold}_{v}", len(bins)-1, bins), v)
    h_pass_above.SetDirectory(0)
    # fail above threshold
    h_fail_above = data_tag.Filter(f"!({probe_selection})& ({probe_var} > {threshold})").Histo1D((f"fail_above{threshold}_{v}", f"fail_above{threshold}_{v}", len(bins)-1, bins), v)
    h_fail_above.SetDirectory(0)

    h_incl = data_tag.Filter(probe_selection).Histo2D((f"incl_{v}", f"incl_{v}", len(bins_probe)-1, bins_probe, len(bins)-1, bins), probe_var, v)
    h_incl.SetDirectory(0)
    h_incl.Sumw2()

    root_file.cd()
    h_pass_below.Write()
    h_pass_above.Write()
    h_fail_below.Write()
    h_fail_above.Write()
    h_incl.Write()
    print(f"[i] histogram {v} written to {out_file_name}")
    h_pass_below.Delete()
    h_fail_below.Delete()

root_file.Close()

PLOT = True
vars = ["L1_mu2_dR", "L1vtx_mu2_dR", "L1_mu1_dR", "L1vtx_mu1_dR"]
probe_name = "p_{T}(#mu_{2})"
lx1, ly1, lx2,ly2 = 0.2, 0.7, 0.5, 0.9
if PLOT:
    for v in vars:
        file = ROOT.TFile(out_file_name)
        # pass probe
        pass_legend = ROOT.TLegend(lx1, ly1, lx2, ly2)
        pass_legend.SetBorderSize(0)
        pass_legend.SetTextSize(0.03)
        pass_legend.SetTextFont(42)
        pass_legend.SetFillColor(0)

        
        h_pass_below   = file.Get(f"pass_below{threshold}_{v}")
        h_pass_below   = utils.style_histogram(h_pass_below,
                                               x_label=config.pretty_name[v],
                                               title=f"pass {probe_name} < {threshold}",
                                               color=ROOT.kBlue,
                                               )
        pass_legend.AddEntry(h_pass_below, f"pass {probe_name} < {threshold}", "l")
        h_pass_above   = file.Get(f"pass_above{threshold}_{v}")
        h_pass_above   = utils.style_histogram(h_pass_above,
                                               x_label=config.pretty_name[v],
                                               title=f"pass {probe_name} > {threshold}",
                                               color=ROOT.kRed,
                                               )
        pass_legend.AddEntry(h_pass_above, f"pass {probe_name} > {threshold}", "l")
        
        cp = ROOT.TCanvas(f"cp_{v}", f"cp_{v}", 800, 800)
        cp.cd()
        h_pass_below.Draw("hist")
        h_pass_above.Draw("hist same")
        pass_legend.Draw("same")
        cp.Update()
        cp.SaveAs(os.path.join(args.output, f"pass_{v}.png"))

        # fail probe
        fail_legend = ROOT.TLegend( lx1, ly1, lx2, ly2)
        fail_legend.SetBorderSize(0)
        fail_legend.SetTextSize(0.03)
        fail_legend.SetTextFont(42)
        fail_legend.SetFillColor(0)

        h_fail_below   = file.Get(f"fail_below{threshold}_{v}")
        h_fail_below   = utils.style_histogram(h_fail_below,
                                               x_label=config.pretty_name[v],
                                               title=f"fail {probe_name} < {threshold}",
                                               color=ROOT.kBlue,
                                               )
        fail_legend.AddEntry(h_fail_below, f"fail {probe_name} < {threshold}", "l")
        h_fail_above   = file.Get(f"fail_above{threshold}_{v}")
        h_fail_above   = utils.style_histogram(h_fail_above,
                                               x_label=config.pretty_name[v],
                                               title=f"fail {probe_name} > {threshold}",
                                               color=ROOT.kRed,
                                               )
        fail_legend.AddEntry(h_fail_above, f"fail {probe_name} > {threshold}", "l")
        cf = ROOT.TCanvas(f"cf_{v}", f"cf_{v}", 800, 800)
        cf.cd()
        h_fail_below.Draw("hist")
        h_fail_above.Draw("hist same")
        fail_legend.Draw("same")
        cf.Update()
        cf.SaveAs(os.path.join(args.output, f"fail_{v}.png"))

        cp.Clear()
        cp.Close()
        cf.Clear()
        cf.Close()
        h_pass_below.Delete()
        h_pass_above.Delete()
        h_fail_below.Delete()
        h_fail_above.Delete()






