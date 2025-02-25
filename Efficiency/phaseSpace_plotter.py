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

    parser = argparse.ArgumentParser(description="Trigger efficiency calculation script")
    
    parser.add_argument('-i', '--input_file', type=str, required=True, 
                        help="Path to the input file")
    parser.add_argument('-o', '--output_file', type=str, required=True, 
                        help="Path to the output file")
    parser.add_argument('-r', '--run', type=str, default=0.5, 
                        help="Era name e.g. 2023C ")
    parser.add_argument('-t', '--tagPath', type=str, required=True,
                        help="HLT_Mu8_v or HLT_Mu4_L1DoubleMu_v")
    parser.add_argument('-p', '--probePath', type=str, required=True,
                        help="HLT_Mu0_L1DoubleMu_v for L1 efficiencies")
    parser.add_argument('--binning', type=str, required=False,
                        help="File json-like to define the binning to evaluate the efficiency" )
    parser.add_argument('--denQ', type=str, required=False,
                        help="Query on the denominator to calculate efficiencies" )
    parser.add_argument('--numQ', type=str, required=False,
                        help="Query on the numerator to calculate efficiencies (in addition to the Probe Muon HLT match)" )
    parser.add_argument('--plot2D', action='store_true', required=False,
                        help="Wether to make also 2D plots" )
    

    args = parser.parse_args()

    tagPath = args.tagPath if args.tagPath else cfg.L1_tag_path
    probePath = args.probePath if args.probePath else cfg.L1_probe_path
    input_file = args.input_file
    run  = args.run
    Name = args.output_file

    denQuery = args.denQ if args.denQ else cfg.default_tagQuery        
    numQuery = args.numQ if args.numQ else cfg.default_probeQuery

    arrays = ['DiMu_mass', 'DiMu_Prob', 'dz_muons' , 'event', '*HLT_*' , 'mu*match', '*lxy*', '*charge*', 'L1*', '*dR*'] 
    arrays+= 'muProbe_pt,muProbe_eta,muProbe_phi,muTag_pt,muTag_eta,muTag_phi'.split(',')
    arrays+= 'L3_muProbe_pt,L3_muProbe_eta,L3_muProbe_phi,L3_muTag_pt,L3_muTag_eta,L3_muTag_phi'.split(',')


    outputdir = os.path.join('Run'+run, Name,'phaseSpace')
    os.makedirs(outputdir, exist_ok=True)
    file = uproot.open(input_file)
    data_np = file[tagPath].arrays( library="np")
    data = pd.DataFrame(data_np)
    
    
    if 'HLT_Mu8' in tagPath and 'HLT_Mu0_L1' in probePath:
        efficiencyText = 'L1 Efficiency'
    elif 'HLT_Mu4_L1' in tagPath and 'HLT_Double' in probePath:
        efficiencyText = 'HLT Efficiency'
    else:
        efficiencyText = 'Efficiency'

    print(f'[INFO] {efficiencyText} : running on {input_file} with tag {tagPath} and probe {probePath}')
    print(f' - TAG query: \n  {denQuery}')
    print(f' - PROBE query: \n  {numQuery}')

    for var1 in cfg.variables:
        print(f'\n ---- plotting {var1} ----')
        fig,ax = plt.subplots(figsize=[15,10])
        hep.cms.label(data=True, label=run, com=13.6)
        ax.grid(True)

        h_all, h_passprob = utils.passfail_histo(data, var1, denQuery, numQuery, probePath, cfg.Bins1d)
        ax.hist(h_all[1][:-1], bins=h_all[1], weights=h_all[0], histtype='step', color='red', linestyle='dashed', label='Pass+Fail')
        ax.hist(h_passprob[1][:-1], bins=h_passprob[1], weights=h_passprob[0], histtype='step', color='blue', linestyle='dashed', label='Pass')
        ax.set_ylabel('Events')
        ax.legend()

        out_name = f'{outputdir}/phaseSpace_Tag{tagPath}_Probe{probePath}_{var1}'
        plt.savefig(f'{out_name}.pdf', bbox_inches='tight')
        plt.savefig(f'{out_name}.png', bbox_inches='tight')
        plt.close()
        print(f' [INFO] saved plot in {out_name}')

        if not args.plot2D:
            continue
        for var in cfg.variables:
            if var1 == var:
                continue
            
            print(f'\n ---- plotting {var1} VS {var} ----')
            fig,ax = plt.subplots(figsize=[15,10])
            hep.cms.label(data=True, label=run, com=13.6)
            ax.grid(True)

            h_all, h_passprob, _ = utils.get_efficiency2D(data, [var1, var], denQuery, numQuery, tagPath, probePath, [cfg.Bins1d[var1], cfg.Bins1d[var]], norm=True)

            # plot the 2D histogram
            plt.figure(figsize=(10,8))
            plt.imshow(h_all[0].T, origin='lower', extent=[h_all[1][0], h_all[1][-1], h_all[2][0], h_all[2][-1]], aspect='auto')
            plt.colorbar(label='Events')
            plt.xlabel(cfg.pretty_name.get(var1, var1))
            plt.ylabel(cfg.pretty_name.get(var, var))
            hep.cms.label(data=True, label=run, com=13.6)
            out_name = f'{outputdir}/phaseSpace_Tag{tagPath}_Probe{probePath}_{var1}_vs_{var}'
            plt.savefig(f'{out_name}.pdf', bbox_inches='tight')
            plt.savefig(f'{out_name}.png', bbox_inches='tight')
            plt.close()