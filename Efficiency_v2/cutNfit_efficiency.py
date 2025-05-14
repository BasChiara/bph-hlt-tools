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
                        help='split by barrel/overlap/endcap eta regions in the selection',
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
    eta_bins['barrel']  =config.eta_barrel
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

        data_sel = data_tag.Filter(' & '.join([eta_selection, dR_selection]))
        print(f'[i] #events after phase space selection: {data_sel.Count().GetValue()}')
        if data_sel.Count().GetValue() == 0:
            print(f'[!] no events in this eta region, skipping')
            continue
        
        this_name = f'{ref_var}_{region}_{dR}'

        # loop over probe-variables
        for var in config.variables:
            print(f'--- variable: {var}')
            bins = array('d', config.Bins1d[var]) if dR == 'dRincl' else array('d', config.Bins1d_tight[var])
            h_eff = ROOT.TH1F(f'h_{var}_{region}_{dR}_efficiency', f'{config.pretty_name[var]} efficiency', len(bins)-1, bins)
            
            for i in range(len(bins)-1):
                print(f'   bin {i}: {bins[i]} - {bins[i+1]}')
                bin_selection = f'(({var}>={bins[i]}) & ({var}<{bins[i+1]}))'

                # pass+fail and pass distribution in the reference variable
                h_tag = data_sel.Filter(bin_selection).Histo1D(
                    (f'h_{this_name}_tag_{i}', config.pretty_name[ref_var], ref_var_bins[0], ref_var_bins[1], ref_var_bins[2]),
                    ref_var
                ).GetValue()
                h_tag.SetDirectory(0)
                h_probe = data_sel.Filter(bin_selection).Filter(probe_selection_).Histo1D(
                    (f'h_{this_name}_probe_{i}', config.pretty_name[ref_var], ref_var_bins[0], ref_var_bins[1], ref_var_bins[2]),
                    ref_var
                ).GetValue()

                Npassfail = h_tag.GetEntries()
                Npass = h_probe.GetEntries()
                eff = Npass/Npassfail if Npassfail > 0 else 0
                if Npassfail > 0:
                    eff_lo, eff_hi = utils.generateClopperPearsonInterval(Npass, Npassfail)
                    eff_elo = eff - eff_lo
                    eff_ehi = eff_hi - eff
                else:
                    eff_ehi = 0
                    eff_elo = 0
                print(f'   N(pass): {Npass} N(pass+fail): {Npassfail}')
                h_eff.SetBinContent(i+1, eff)
                h_eff.SetBinError(i+1, (eff_elo + eff_ehi)/2.0)

                root_file.cd()
                h_tag.Write()
                h_probe.Write()

                h_tag.Delete()
                h_probe.Delete()
            
            print(f'[o] save histogram {h_eff.GetName()}')
            h_eff = utils.style_efficiency(h_eff, x_label=config.pretty_name[var])      
            h_eff.Write()

root_file.Close()
print(f'[i] output file closed: {out_file_name}')


    