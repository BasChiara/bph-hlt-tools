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

Eff2ds = False
plt.style.use(hep.style.CMS)


extra_cuts = dict(
    muProbe_pt = ['abs(muProbe_eta)<1.5', 
                  'abs(muProbe_eta)>1.5', 
                  '0<abs(muProbe_eta)<0.9', 
                  '0.9<abs(muProbe_eta)<1.2', 
                  '1.2<abs(muProbe_eta)<2.4'],
    muProbe_eta = [
                'muProbe_pt>4',
                'muProbe_pt>6',
                'muProbe_pt>8',
    ],

    muProbe_phi = [
                'muProbe_pt>6',
                'muProbe_pt>6 & abs(muProbe_eta)>1.5',
                'muProbe_pt>8',
                'muProbe_pt>8 & abs(muProbe_eta)>1.5',
    ]
)
extra_cuts = dict()

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

    args = parser.parse_args()

    tagPath = args.tagPath if args.tagPath else cfg.L1_tag_path
    probePath = args.probePath if args.probePath else cfg.L1_probe_path
    input_file = args.input_file
    run  = args.run
    Name = args.output_file

    denQuery = args.denQ if args.denQ else cfg.default_tagQuery        
    numQuery = args.numQ if args.numQ else cfg.default_probeQuery

    arrays = ['DiMu_mass', 'DiMu_Prob', 'event', '*HLT_*' , 'mu*match', '*lxy*', '*charge*', 'L1*', '*dR*'] #+ ['DiMu_Prob']
    arrays+= 'muProbe_pt,muProbe_eta,muProbe_phi,muTag_pt,muTag_eta,muTag_phi'.split(',')
    arrays+= 'L3_muProbe_pt,L3_muProbe_eta,L3_muProbe_phi,L3_muTag_pt,L3_muTag_eta,L3_muTag_phi'.split(',')


    outputdir = os.path.join('Run'+run, Name)
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

    print(f'{efficiencyText} : running on {input_file} with tag {tagPath} and probe {probePath}')
    print(f' TAG query: {denQuery}')
    print(f' PROBE query: {numQuery}')

    for var1 in cfg.variables:
        
        print(f' ---- 1D efficiency VS {var1} ----')
        
        bins, ratio, err = utils.get_and_store(
            data=data,
            var=var1,
            denQuery=denQuery,
            numQuery=numQuery,
            tagPath=tagPath,
            probePath=probePath,
            Bins1d = cfg.Bins1d,
            input_file=input_file,
            outputdir=outputdir,
        )
        
        bin_mean = (bins[1:] + bins[:-1])/2
        bin_size = (bins[1:] - bins[:-1])/2

        
        fig,ax = plt.subplots(figsize=[15,10])
        ax.errorbar(bin_mean, ratio, err, xerr=bin_size, ls='none', marker='o', capsize=2 )    
        ax.set_ylabel(efficiencyText)
        ax.set_xlabel(cfg.pretty_name.get(var1, var1))
        hep.cms.label(data=True, label=run, com=13.6)
        ax.set_ylim(0, 1.2)
        ax.grid(True)
        plt.savefig(f'{outputdir}/Tag{tagPath}_Probe{probePath}_{var1}.pdf', bbox_inches='tight')
        plt.close()

        
        if var1 in extra_cuts:
            for indx, extra in enumerate(extra_cuts[var1]):
                denQuery_extra = denQuery+' and '+extra
                utils.get_and_store(
                    data=data, 
                    var=var1,
                    denQuery=denQuery_extra,
                    numQuery=numQuery, 
                    tagPath=tagPath, 
                    probePath=probePath, 
                    Bins1d = cfg.Bins1d,
                    input_file=input_file,
                    outputdir=outputdir,
                    v_name=f'v{indx}')

        for var2 in cfg.variables:            
            if not Eff2ds: continue
            if var2 == var1: continue

            print(f' ---- 2D efficiency VS {var1} VS {var2} ----')
            xedges = np.array(cfg.Bins1d[var1])
            yedges = np.array(cfg.Bins1d[var2])
            H_num, _, _ = np.histogram2d(data.query(numQuery+" & "+numQuery )[var1], data.query(numQuery+" & "+numQuery )[var2], bins=[xedges, yedges], weights=data.query(numQuery)[f'muProbe_{probePath}'])
            H_denum, _, _ = np.histogram2d(data.query(numQuery)[var1], data.query(numQuery)[var2], bins=[xedges, yedges])
            ratio = np.divide(H_num, H_denum, out=np.zeros_like(H_num), where=H_denum != 0)

            # Plotting with matplotlib
            plt.figure(figsize=(10, 8))
            plt.imshow(ratio.T, origin='lower', aspect='auto', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], cmap='viridis')
            xcenters = 0.5 * (xedges[:-1] + xedges[1:])
            ycenters = 0.5 * (yedges[:-1] + yedges[1:])


            for i in range(ratio.shape[0]):
               for j in range(ratio.shape[1]):
                   bin_center_x = xcenters[i]
                   bin_center_y = ycenters[j]
                   # Adjust the annotation to center it in the cell
                   text = plt.text(bin_center_x, bin_center_y, round(ratio[i, j], 3),
                       ha="center", va="center", color="black", fontsize=10)


            plt.colorbar(label='L1 Efficiency')
            plt.xlabel(cfg.pretty_name.get(var1, var1))
            plt.ylabel(cfg.pretty_name.get(var2, var2))
            hep.cms.label(data=True, label=run, com=13.6)
            plt.savefig(f'{outputdir}/Tag{tagPath}_Probe{probePath}_{var1}_vs_{var2}.pdf', bbox_inches='tight')
            plt.close()


