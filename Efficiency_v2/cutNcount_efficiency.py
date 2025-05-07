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
argparser.add_argument('--splitEta',
                        action='store_true',
                        help='split by barrel/overlap/endcap eta regions for the probe muon',
                        )
argparser.add_argument('--splitDR',
                        action='store_true',
                        help='split by deltaR between tag and probe muon',
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
out_file_name = os.path.join(args.output, f'efficiency_{data_tag}.root')
print(f'[i] output file: {out_file_name}')

# check how many files are in the directory
data_files = []
for dataset in data_info['dataset']:
    print(f' - dataset : {dataset}')
    file_list = glob.glob(data_info['dataset'][dataset])
    print(f'   #file(s) = {len(file_list)}')
    data_files.extend(file_list)

# root dataframe for data
data_tag = ROOT.RDataFrame(data_info["tree"], data_files).Filter(tag_selection_).Define('DiMu_mu2_aeta', 'fabs(DiMu_mu2_eta)')
print(f'[i] #events after TAG selection: {data_tag.Count().GetValue()}')

# set eta bins
eta_bins = {'cms' : [0, 2.4]}
if args.splitEta:
    eta_bins['barrel']  = config.eta_barrel
    eta_bins['overlap'] = config.eta_overlap
    eta_bins['endcap']  = config.eta_endcap
# set deltaR bins
deltaR_bins = {'dRincl' : [0, 1.2]}
if args.splitDR:
    deltaR_bins = config.deltaR_bins

# variable to "fit"
ref_var = 'DiMu_mass'
ref_var_bins = [40, 2.9 , 3.3]

root_file = ROOT.TFile(out_file_name, 'RECREATE')
print('\n')
# loop over eta bins
for region, eta_range in eta_bins.items():
    eta_selection = f'((DiMu_mu2_aeta>{eta_range[0]}) & (DiMu_mu2_aeta<{eta_range[1]}))'
    print(f'- eta region: {region} -> {eta_selection}')

    for dR, dR_range in deltaR_bins.items():
        dR_selection = f'((DiMu_dR>{dR_range[0]}) & (DiMu_dR<{dR_range[1]}))'
        print(f'-- deltaR region: {dR} -> {dR_selection}')

        data_sel = data_tag.Filter(eta_selection).Filter(dR_selection)
        print(f'[i] #events after phase space selection: {data_sel.Count().GetValue()}')
        if (data_sel.Count().GetValue() == 0):
            print(f'[i] no events in this selection, skipping')
            continue

        # loop over probe-variables
        for var in config.variables:
            print(f'--- variable: {var}')
            bins = array('d', config.Bins1d[var]) if dR_range[0] < 0.4 else array('d', config.Bins1d_tight[var])

            this_name = f'{var}_{region}_{dR}'

            h_eff = ROOT.TH1F(f'h_{this_name}_efficiency', f'{config.pretty_name[var]} efficiency', len(bins)-1, bins)
            
            # create histogram for the variable
            h_tag = data_sel.Histo1D(
                (f'h_{this_name}_tag', config.pretty_name[var], len(bins) -1 , bins),
                var
            ).GetValue()
            h_tag.SetDirectory(0)
            h_tag.Sumw2()

            h_probe = data_sel.Filter(probe_selection_).Histo1D(
                (f'h_{this_name}_probe', config.pretty_name[var], len(bins) -1 , bins),
                var
            ).GetValue()
            h_probe.SetDirectory(0)
            h_probe.Sumw2()
            
            g_eff, h_eff = utils.efficiency_from_histo(h_tag, h_probe, args.verbose)
            g_eff        = utils.style_efficiency(g_eff, x_label=config.pretty_name[var])
            h_eff        = utils.style_efficiency(h_eff, x_label=config.pretty_name[var])
            g_eff.SetName(f'Graph_{this_name}_efficiency' + ('MC' if data_info['isMC'] else 'Data'))
            h_eff.SetName(f'Hist_{this_name}_efficiency' + ('MC' if data_info['isMC'] else 'Data'))
            

            root_file.cd()
            h_tag.Write()
            h_probe.Write()
            g_eff.Write()
            h_eff.Write()
    
    print('\n')

root_file.Close()
print(f'[i] output file closed: {out_file_name}')


    