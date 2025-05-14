#!/usr/bin/env python3
import ROOT
ROOT.gROOT.SetBatch(True)  # No display

import argparse
import json
from array import array

import os
import sys

def make_efficiency_hists(json_file, dR_region = 'dRincl', trigger ='L1'):

    with open(json_file) as f:
        data = json.load(f)

    # eta regions skipping the inclusive plot
    cats = [cat for cat in data if cat != "cms"]

    # common pT bin edges
    pt_edges = data[cats[0]][dR_region]["DiMu_mu2_pt_bins"]
    nbins_x = len(pt_edges) - 1

    # 4) build η edges by stitching the eta_bin ranges of each category
    eta_edges = [ data[cat]["eta_bin"][0] for cat in cats ]
    # append the upper edge of the last category
    eta_edges.append( data[cats[-1]]["eta_bin"][1] )
    nbins_y = len(eta_edges) - 1

    # convert to C-style float arrays
    pt_arr  = array('f', pt_edges)
    eta_arr = array('f', eta_edges)

    # 2D histograms
    x_label = "probe #mu p_{T} (GeV)"
    y_label = "probe #mu |#eta|"
    h_MC   = ROOT.TH2F("h_eff_MC",   f"MC {trigger} efficiency; {x_label}; {y_label}",
                       nbins_x, pt_arr, nbins_y, eta_arr)
    h_data = ROOT.TH2F("h_eff_data", f"Data Efficiency; {x_label}; {y_label}",
                       nbins_x, pt_arr, nbins_y, eta_arr)
    h_sf   = ROOT.TH2F("h_eff_sf",   f"{trigger} scale factors; {x_label}; {y_label}",
                       nbins_x, pt_arr, nbins_y, eta_arr)

    # 6) fill them
    for j, cat in enumerate(cats):
        eff_mc          = data[cat][dR_region]["eff_MC"]
        eff_mc_err      = data[cat][dR_region]["eff_MC_err"]
        eff_data        = data[cat][dR_region]["eff_data"]
        eff_data_err    = data[cat][dR_region]["eff_data_err"]
        sf              = data[cat][dR_region]["sf"]
        sf_err          = data[cat][dR_region]["sf_err"]

        for i in range(nbins_x):
            #print(f"Filling bin {i+1} in category {cat} (bin edges: {pt_edges[i]}, {pt_edges[i+1]})")
            binx = i+1
            biny = j+1
            # MC
            h_MC.SetBinContent(binx, biny, eff_mc[i])
            h_MC.SetBinError(  binx, biny, eff_mc_err[i])
            # Data
            h_data.SetBinContent(binx, biny, eff_data[i])
            h_data.SetBinError(  binx, biny, eff_data_err[i])
            # SF
            h_sf.SetBinContent(binx, biny, sf[i])
            h_sf.SetBinError(  binx, biny, sf_err[i])
    
    axis_title_size = 0.06
    h_MC.GetXaxis().SetTitleSize(axis_title_size)
    h_MC.GetYaxis().SetTitleSize(axis_title_size)
    h_MC.GetZaxis().SetRangeUser(0.0, 1.0)
    h_data.GetXaxis().SetTitleSize(axis_title_size)
    h_data.GetYaxis().SetTitleSize(axis_title_size)
    h_data.GetZaxis().SetRangeUser(0.0, 1.0)
    h_sf.GetXaxis().SetTitleSize(axis_title_size)
    h_sf.GetYaxis().SetTitleSize(axis_title_size)
    h_sf.GetZaxis().SetRangeUser(0.6, 1.4)
            
    return h_MC, h_data, h_sf

def main(json_file, trigger):
    
    if not os.path.exists(json_file):
        print(f"Error: Base path {base_path} does not exist.")
        sys.exit(1)
    base_path = os.path.dirname(os.path.abspath(json_file))
    
    h_MC, h_data, h_sf = make_efficiency_hists(json_file, dR_region='dRincl', trigger=trigger)
    
    outf = ROOT.TFile(f"{base_path}/efficiencies_{trigger}.root", "RECREATE")
    h_MC.Write()
    h_data.Write()
    h_sf.Write()
    outf.Close()
    print(f"[o] saved efficiencies to {outf.GetName()}")

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPaintTextFormat(".2f")
    ROOT.gStyle.SetNumberContours(255)

    for hist, name in [(h_MC, "MC"), (h_data, "data"), (h_sf, "SF")]:
        c = ROOT.TCanvas("c_"+name, hist.GetTitle(), 1000, 550)
        hist.Draw("COLZ TEXT90")
        c.SaveAs(f"{base_path}/efficiency_{name}.png")
        c.SaveAs(f"{base_path}/efficiency_{name}.pdf")
        print(f"Saved efficiency_{name}.png")

if __name__ == "__main__":
    # Set up argument parser

    parser = argparse.ArgumentParser(description="Create efficiency histograms from JSON summary file.")
    parser.add_argument("--json_file", type=str, help="Path to the JSON summary file.")
    parser.add_argument("--trigger", type=str, choices=['L1', 'HLT'], help="Trigger name to use for the histograms.")
    args = parser.parse_args()

    main(args.json_file, args.trigger)
