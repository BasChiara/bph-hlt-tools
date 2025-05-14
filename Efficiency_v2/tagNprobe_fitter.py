#!/usr/bin/env python
import ROOT
ROOT.gROOT.SetBatch(True)  # No graphics
svc = ROOT.RooMsgService.instance()
# only show WARNING or above:
svc.setGlobalKillBelow(ROOT.RooFit.WARNING)
# turn off the “Minimization” category entirely
svc.setStreamStatus(ROOT.RooFit.Minimization, False)
# ─────────────────────────────────────────────────────────────
from ROOT import RooFit, RooRealVar, RooDataHist, RooArgList, \
                 RooGaussian, RooChebychev, RooPolynomial, RooExponential, RooAddPdf

import os
import sys
import json
import array
import numpy as np

import argparse

import config as config
import utils as utils

SYS_FROM_CUTNCOUNT = False

def fit_double_gauss(histo, name):
    if not histo:
        print(f"[{name}] Missing histogram; skipping.")
        return None, None, 0.0, 0.0, None
    if histo.Integral() == 0:
        print(f"[{name}] Empty histogram; skipping.")
        return None, None, 0.0, 0.0, None
    """Builds a double-Gaussian + linear-bkg, fits it,
       returns (RooPlot frame, signalYield, signalError)."""
    
    mass = RooRealVar("mass", "m(#mu#mu) [GeV]", 2.9, 3.3)
    data = RooDataHist(f"data_{name}", '', RooArgList(mass), histo)

    # -- signal: two Gaussians, shared mean
    mean   = RooRealVar(f"mean_{name}",   "mean",  3.10, 3.09, 3.11)
    sigma1 = RooRealVar(f"sigma1_{name}", "sigma1",    0.015, 0.01, 0.1)
    sigma2 = RooRealVar(f"sigma2_{name}", "sigma2",    0.055, 0.01, 0.2)
    frac   = RooRealVar(f"frac_{name}",   "frac",  0.7,   0.0,   1.0)

    g1 = RooGaussian(f"g1_{name}", "gauss1", mass, mean, sigma1)
    g2 = RooGaussian(f"g2_{name}", "gauss2", mass, mean, sigma2)
    sig = RooAddPdf( f"sig_{name}", "double-Gauss",
                     RooArgList(g1, g2),
                     RooArgList(frac) )

    # -- background: linear Chebychev
    a0  = RooRealVar(f"a0_{name}", "a0", 0.0, -5.0, 5.0)
    a1  = RooRealVar(f"a1_{name}", "a1", 0.0, -1.0, 1.0)
    bkg = RooExponential(f"bkg_{name}", "bkg", mass, a0)
    #bkg = RooPolynomial(f"bkg_{name}", "bkg", mass, RooArgList(a0))
    #bkg = RooChebychev(f"bkg_{name}", "bkg", mass, RooArgList(a0, a1))

    # -- extended model: Nsig * sig + Nbkg * bkg
    tot = histo.Integral()
    Ns  = RooRealVar(f"Ns_{name}", "N_{signal}", tot*0.5, 0, 2*tot)
    Nb  = RooRealVar(f"Nb_{name}", "N_{bkg}"   , tot*0.5, 0, 2*tot)
    model = RooAddPdf( f"model_{name}", "sig+bkg",
                       RooArgList(sig, bkg),
                       RooArgList(Ns, Nb) )

    # -- fit
    fr = model.fitTo(data,
                    RooFit.Extended(True),
                    RooFit.SumW2Error(True),
                    RooFit.Save(True),
                    RooFit.PrintLevel(-1))
    # -- parse results
    if fr.status() != 0:
        print(f"[{name}] Fit failed with status {fr.status()}; skipping.")
    
    pars = fr.floatParsFinal()
    npar = pars.getSize()
    pars_dict = {}
    pars_dict["status"] = fr.status()
    for i in range(npar):
        rv    = pars.at(i)                 # returns a RooRealVar*
        name  = rv.GetName()
        val   = rv.getVal()
        err   = rv.getError()
        pars_dict[name] = (val, err)
        

    # -- frame for plotting
    frame = mass.frame(RooFit.Title(''))
    data.plotOn(frame)
    model.plotOn(frame,
                 RooFit.MoveToBack()
                 )  # total
    chi2_ndf = frame.chiSquare(npar)
    pars_dict["chi2/ndf"] = (chi2_ndf, -1)

    return frame, model, Ns.getVal(), Ns.getError(), pars_dict

def TLatex_param(x0, y0, params, is_tag=True):
    
    t = ROOT.TLatex()
    t.SetTextSize(0.08)
    t.SetTextAlign(12)
    t.SetTextColor(ROOT.kBlack)
    t.SetTextFont(42)
    t.SetNDC()
    
    i = 0
    dy = 0.07
    x = x0 #+ 0.25 * (i % 2)
    for par in params:
        if 'Nb_' in par: nice_name = "N_{bkg}"
        elif 'Ns_' in par: nice_name = "N_{sig}"
        elif 'mean_' in par: nice_name = "mean"
        elif 'chi2/ndf' in par: nice_name = "#chi^{2}/ndf"
        else: continue
        nice_name += "^{TAG}" if is_tag else "^{PRB}"
        text = f"{nice_name} = {params[par][0]:.3f} #pm {params[par][1]:.3f}" if params[par][1] > 0 else f"{nice_name} = {params[par][0]:.3f}" 
        y = y0 - dy * i
        i += 1
        t.DrawLatex(x, y, text)

    t.DrawLatex(x, y, text)
    return t

def TLatex_info(x0, y0, text):
    t = ROOT.TLatex()
    t.SetTextSize(0.1)
    t.SetTextAlign(12)
    t.SetTextColor(ROOT.kBlack)
    t.SetTextFont(42)
    t.SetNDC()
    
    x = x0
    y = y0
    t.DrawLatex(x, y, text)

# ----- FITTER ----- 

# parse command line arguments
parser = argparse.ArgumentParser(description='Fit tag and probe histograms.')
parser.add_argument('--input', type=str, required=True,
                    help='Input ROOT file containing histograms.')
parser.add_argument('--output', type=str, required=True,
                    help='Output directory for saving plots and results.')
parser.add_argument('-t', '--tag', type=str, default='')
args = parser.parse_args()

# -- output directory
output_dir = args.output
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
output_plot = os.path.join(output_dir, "plots")
if not os.path.exists(output_plot):
    os.makedirs(output_plot)

tag = '_'.join([
    args.tag, 
    'sysCount' if SYS_FROM_CUTNCOUNT else 'sysFit',
])

# -- input ROOT file
input_file = args.input
if not os.path.isfile(input_file):
    print(f"Error: Input file '{input_file}' does not exist.")
    sys.exit(1)
f = ROOT.TFile.Open(input_file)

# --- loop over eta regions
regions = ["cms", "barrel", "overlap", "endcap"]

# --- bins
ref_var = 'DiMu_mu2_pt'
ref_varbins = config.Bins1d[ref_var]
bin_edges = [[ref_varbins[i], ref_varbins[i+1]] for i in range(len(ref_varbins)-1)]
bin_centers = [(b[0]+b[1])/2.0 for b in bin_edges]
n_idx = len(bin_centers)
print(f"Bin centers: {bin_centers}")

# --- efficiency
cutncount_eff   = {}
result_eff      = { r: [] for r in regions }
result_eff_err  = { r: [] for r in regions }

# --- results
result_dict = {r : {} for r in regions}

# bad fits
whatch_list = {r : [] for r in regions}
chi_thresh = 3.0
status_thresh = 1000

for region in regions:
    print(f"\n --- fitting region: {region} ---")
    
    result_dict[region] = {
        "bin_edges": ref_varbins,
        "bin_centers": bin_centers,
        "efficiency"        : [],
        "efficiency_toterr" : [],
        "efficiency_staterr": [],
        "efficiency_syserr" : [],
    }
    # --- systematic uncertainties - cut&count
    h_eff_cutncount = f.Get(f"h_{ref_var}_{region}_dRincl_efficiency")
    if not h_eff_cutncount:
        print(f"[{region}] missing cut&count efficiency histogram --> skipping")
        continue
    h_eff_cutncount.SetDirectory(0)

    for i in range(n_idx):
        tag_name   = f"h_DiMu_mass_{region}_dRincl_tag_{i}"
        probe_name = f"h_DiMu_mass_{region}_dRincl_probe_{i}"
        h_tag   = f.Get(tag_name)
        h_probe = f.Get(probe_name)
        if not h_tag or not h_probe:
            print(f"[{region}][{i}] Missing histos; skipping.")
            result_dict[region]['efficiency'].append(-1)
            continue
        
        # ---- fit histograms ----
        frame_tag, model_tag, Ntag, Etag, pars_tag = fit_double_gauss(h_tag,   f"{region}_tag_{i}")
        frame_prb, model_prb, Nprb, Eprb, pars_prb = fit_double_gauss(h_probe, f"{region}_prb_{i}")
        
        # check fit status
        if pars_tag and (pars_tag["status"] > status_thresh or pars_tag["chi2/ndf"][0] > chi_thresh):
            whatch_list[region].append(i)
            print(f"[{region}][{i}] Fit failed with chi2/ndf={pars_tag['chi2/ndf'][0]:.3f}; skipping.")
            continue
        if pars_prb and (pars_prb["status"] > status_thresh or pars_prb["chi2/ndf"][0] > chi_thresh):
            whatch_list[region].append(i)
            print(f"[{region}][{i}] Fit failed with chi2/ndf={pars_prb['chi2/ndf'][0]:.3f}; skipping.")
            continue
        
        # compute and store probe/tag efficiency
        if SYS_FROM_CUTNCOUNT:
            eff_val, eff_elo, eff_ehi = utils.calc_efficiency_err(Nprb, Ntag)
            eff_e = (eff_ehi + eff_elo) / 2.0
            eff_sys = h_eff_cutncount.GetBinContent(i+1)
        else:
            eff_val = h_eff_cutncount.GetBinContent(i+1)
            eff_e = h_eff_cutncount.GetBinError(i+1)
            eff_elo = eff_e
            eff_ehi = eff_e
            eff_sys = utils.calc_efficiency_err(Nprb, Ntag)[0]

        result_dict[region]['efficiency'].append(eff_val)
        result_dict[region]['efficiency_staterr'].append(eff_e)
        
        delta_eff = abs(eff_sys - eff_val)
        result_dict[region]['efficiency_syserr'].append(delta_eff)
        
        result_dict[region]['efficiency_toterr'].append(np.sqrt(eff_e**2 + delta_eff**2))
        print(f"[{region}][{i}] Tag={Ntag:.1f}±{Etag:.1f}, "
              f"Probe={Nprb:.1f}±{Eprb:.1f}, eff={eff_val:.3f} -{eff_elo:.3f} +{eff_ehi:.3f} (stat) ± {delta_eff:.3f} (syst)")

        # --- plot fits ---
        
        c = ROOT.TCanvas(f"c_{region}_{i}", f"{region} idx={i}", 1000, 500)
        c.cd()
        
        txtpad_x1, txtpad_w = 0.0, 0.3
        fit_pad_w = (1.0 - txtpad_w)/2.0
        pad_top, pad_bottom = 1.0, 0.0 
        pad_margin = [0.15, 0.02, 0.1, 0.05] 
        
        # pad for fit summary
        textpad = ROOT.TPad(f"textpad_{region}_{i}", f"{region} idx={i}", 
                            txtpad_x1, pad_bottom, txtpad_x1+txtpad_w, pad_top
                            )
        textpad.Draw()
        # pads for tag and probe
        tagpad = ROOT.TPad(f"tagpad_{region}_{i}", f"{region} idx={i}", 
                            txtpad_x1+txtpad_w, pad_bottom, txtpad_x1+txtpad_w+fit_pad_w, pad_top 
                           )
        tagpad.SetMargin(pad_margin[0], pad_margin[1], pad_margin[2], pad_margin[3])
        tagpad.Draw()
        
        probepad = ROOT.TPad(f"probepad_{region}_{i}", f"{region} idx={i}",
                             txtpad_x1+txtpad_w+fit_pad_w, pad_bottom, txtpad_x1+txtpad_w+2*fit_pad_w, pad_top
                             )
        probepad.SetMargin(pad_margin[0], pad_margin[1], pad_margin[2], pad_margin[3])
        probepad.Draw()
        
        # --- left: tag
        tagpad.cd()
        if frame_tag: frame_tag.Draw()
        # --- right: probe
        probepad.cd()
        if frame_prb: frame_prb.Draw()
        # --- text pad
        textpad.cd()
        x0, y0, dY = 0.04, 0.90, 0.08

        TLatex_info(x0, y0, 
                    f"{config.eta_bins[region][0]} < |#eta| < {config.eta_bins[region][1]}")
        TLatex_info(x0, y0-dY,
                    f"{bin_edges[i][0]} < p_{{T}}(#mu_{{PRB}}) < {bin_edges[i][1]}")
       # TLatex_info(x0, 0.85,
       #             f"{config.deltaR_bins['dRincl'][0]} < #Delta R < {config.deltaR_bins['dRincl'][1]}")
        TLatex_info(x0, y0-2*dY,
                    f"#varepsilon = {eff_val:.3f} #pm {(eff_ehi+eff_elo)/2:.3f} ")
        if pars_prb : TLatex_param(x0, 0.6, pars_prb, is_tag=False)
        if pars_tag : TLatex_param(x0, 0.3, pars_tag, is_tag=True)

        c.Update()
        c.SaveAs(f"{output_plot}/{region}_{i}_fit.pdf")
        c.SaveAs(f"{output_plot}/{region}_{i}_fit.png")
f.Close()

# save efficiencies to JSON
print("\n --- saving efficiencies to JSON file ---")
out_json = os.path.join(output_dir, f"efficiency_fit_{tag}.json")
with open(out_json, "w") as f:
    json.dump(result_dict, f, indent=4,separators=(", ", ": "),)
f.close()
print(f" Saved efficiencies to JSON file {out_json}")

# fit report
print("Bad fits:")
for region in regions:
    if len(whatch_list[region]) > 0:
        print(f"  {region}: {whatch_list[region]}")
    else:
        print(f"  {region}: None")

# save efficiencies histograms
print("\n --- saving efficiencies to ROOT file ---")
out_root = out_json.replace(".json", ".root")
file_out = ROOT.TFile(out_root, "RECREATE")
for region in regions:
    print(f"\n --- plotting efficiencies for region: {region} ---")
    name = f'h_{ref_var}_{region}_dRincl_efficiency'
    h_eff = ROOT.TH1F(name, '', n_idx, array.array('d', config.Bins1d[ref_var]))
    for i in range(n_idx):
        if result_dict[region]['efficiency'][i] < 0:
            continue
        h_eff.SetBinContent(i+1, result_dict[region]['efficiency'][i])
        tot_err = np.sqrt(result_dict[region]['efficiency_staterr'][i]**2 + result_dict[region]['efficiency_syserr'][i]**2)
        tot_err = min(tot_err, 1.0 - result_dict[region]['efficiency'][i])
        h_eff.SetBinError(i+1, tot_err)
    h_eff = utils.style_efficiency(h_eff, config.pretty_name[ref_var])
    h_eff.Write()
file_out.Close()
print(f"Saved efficiencies to ROOT file: {out_root}")

    
