import pandas as pd
import matplotlib.pyplot as plt
import mplhep as hep
import uproot
import seaborn as sns

import os
import numpy as np
import json

import argparse
import sys

# custom functions
import config as cfg
import utils as utils

plt.style.use(hep.style.CMS)


if __name__== '__main__':

    parser = argparse.ArgumentParser(description='Compare efficiency between two triggers')
    parser.add_argument('-i', '--input', help='input settings file', required=True)
    args = parser.parse_args()

    input_settings = args.input
    
    if os.path.exists(input_settings):
        with open(input_settings) as f:
            settings = json.load(f)
    else:
        print(f'Error: file {input_settings} not found')
        sys.exit(1)
    
    var = settings['var']
    output_label = settings['output_label']
    outputdir = 'plots'
    
    
    inputs = settings.get('input_files', None)
    legend_text = settings.get('legend_text', None)
    if not inputs:
        print(f'Error: inputs not found in {input_settings}')
        sys.exit(1)
    name = []
    tag = []
    probe = []
    efficiency = []
    error = []
    bins = []


    for key, file in inputs.items():
        if os.path.exists(file):
            print(f'[+] reading file {file}')
            with open(file) as f:
                input_data = json.load(f)
        else:
            print(f'Error: file {file} not found')
            sys.exit(1)

        var = input_data['Var']
        
        # tag & probe paths
        tagPath     = input_data['Tag'] 
        probePath   = input_data['Probe']
        if 'HLT_Mu8' in tagPath and 'HLT_Mu0_L1' in probePath:
            efficiencyText = 'L1 Efficiency'
        elif 'HLT_Mu4_L1' in tagPath and 'HLT_Double' in probePath:
            efficiencyText = 'HLT Efficiency'
        else:
            efficiencyText = 'Efficiency'


        print(f' - {efficiencyText} : TAG {tagPath} and PROBE {probePath}')

        bins.append(input_data['Bins'])
        name.append(key)
        tag.append(tagPath)
        probe.append(probePath)
        efficiency.append(input_data['Ratio'])
        error.append(input_data['Error'])
        
    # check if all the bins are the same
    bin_ref = np.array(bins[0], dtype=float)
    bin_mean = (bin_ref[1:] + bin_ref[:-1])/2
    bin_size = (bin_ref[1:] - bin_ref[:-1])/2
    # plot
    fig,ax = plt.subplots(figsize=[15,10])
    ax.set_ylabel(efficiencyText)
    ax.set_xlabel(cfg.pretty_name.get(var, var))
    hep.cms.label(data=True, label=settings.get('run', ''), com=13.6)
    ax.set_ylim(0, 1.2)
    ax.grid(True)
    [ax.errorbar(bin_mean, efficiency[i], error[i], xerr=bin_size, ls='none', marker='o', capsize=2, label=legend_text[run] if legend_text else run) for i, run in enumerate(name)]
    ax.legend()
    plot_name = f'{outputdir}/compareEfficiency_Tag{tagPath}_Probe{probePath}_{var}_{output_label}'
    plt.savefig(plot_name+'.png', bbox_inches='tight')
    plt.savefig(plot_name+'.pdf', bbox_inches='tight')
    plt.close()
    print(f'\n[->] plot saved in {plot_name}')


