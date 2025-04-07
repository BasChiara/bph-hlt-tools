import ROOT
ROOT.gStyle.SetOptStat(0)
ROOT.ROOT.EnableImplicitMT()
ROOT.gROOT.SetBatch(True)

import argparse
import json
import glob
import pandas as pd
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
out_file_name = os.path.join(args.output, f'efficiency_L1seed_{data_tag}.root')
print(f'[i] output file: {out_file_name}')

# check how many files are in the directory
data_files = []
for dataset in data_info['dataset']:
    print(f' - dataset : {dataset}')
    file_list = glob.glob(data_info['dataset'][dataset])
    print(f'   #file(s) = {len(file_list)}')
    data_files.extend(file_list)

# root dataframe for data
data_tag = ROOT.RDataFrame(data_info["tree"], data_files).Filter(tag_selection_)
Nevents = data_tag.Count().GetValue()
print(f'[i] #events after TAG selection: {Nevents}')

# loop on L1 seeds and see which is the most fired
columns = ['L1_seed', 'n_pass', 'fraction']
data_list = []
var = config.variables[0]
root_file = ROOT.TFile(out_file_name, 'RECREATE')
for seed in config.L1_seeds:
    print(f'[i] processing seed: {seed}')
    # L1 seed selection
    L1_selection = f'({seed} == 1)'
    
    n_pass = data_tag.Filter(L1_selection).Count().GetValue()
    print(f' - events passing L1 seed: {n_pass/Nevents:.4f}')
    data_list.append({'L1_seed': seed, 'n_pass': n_pass, 'fraction': n_pass/Nevents})
    L1_selection = f'({seed} == 0)'
    if (n_pass/Nevents) < 0.1: continue
    # get efficiency curve
    print(f' - variable: {var}')
    bins = array('d', config.Bins1d[var])
    # create histogram for the variable
    h_tag = data_tag.Histo1D(
        (f'h_{var}_{seed}_tag', config.pretty_name[var], len(bins) -1 , bins),
          var
    ).GetValue()
    h_tag.SetDirectory(0)
    h_tag.Sumw2()

    h_probe = data_tag.Filter('&'.join([probe_selection_, L1_selection])).Histo1D(
        (f'h_{var}_{seed}_probe', config.pretty_name[var], len(bins) -1 , bins),
        var
    ).GetValue()
    h_probe.SetDirectory(0)
    h_probe.Sumw2()
    
    g_eff, h_eff = utils.efficiency_from_histo(h_tag, h_probe, args.verbose)
    #g_eff = utils.style_efficiency(g_eff, x_label=config.pretty_name[var])
    #h_eff = utils.style_efficiency(h_eff, x_label=config.pretty_name[var])
    g_eff.SetName(f'Graph_efficiency_{seed}_' + ('MC' if data_info['isMC'] else 'Data'))
    h_eff.SetName(f'Hist_efficiency_{seed}_' + ('MC' if data_info['isMC'] else 'Data'))

    root_file.cd()
    h_tag.Write()
    h_probe.Write()
    g_eff.Write()
    h_eff.Write()
    
root_file.Close()

df = pd.DataFrame(data_list, columns=columns)
df = df.sort_values(by='fraction', ascending=False, ignore_index=True)
print(df)
df.to_csv('L1seed_efficiency.csv', index=False)