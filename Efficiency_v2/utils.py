import ROOT
ROOT.ROOT.EnableImplicitMT()
ROOT.gROOT.SetBatch(True)
import array
import numpy as np
import json
import os

def build_selection(sel_list):
    # check is a list
    if not isinstance(sel_list, list):
        sel_list = [sel_list]
    if not sel_list:
        return '(1)'
    return '&'.join(sel_list)


def selection_from_json(file):
    tag_selection_  = None
    probe_selection_ = None
    name = None
    try:
        with open(file) as f:
            selection = json.load(f) 
            tag_selection_   = build_selection(selection['tag_selection'])
            probe_selection_ = build_selection(selection['probe_selection'])
            name = selection['name']
    except:
        if os.path.exists(file):
            print(f'Error: {file} is not a valid json file')
            
    return tag_selection_, probe_selection_, name

def get_hist_fromFile(file_name, handle = '', category = 'efficiency'):
    if not os.path.exists(file_name):
        print(f'Error: {file_name} does not exist')
        return None
    f = ROOT.TFile.Open(file_name)
    if not f:
        print(f'Error: {file_name} is not a valid root file')
        return None
    for e in f.GetListOfKeys():
        if not 'TH1' in e.GetClassName()  : continue
        if not category in e.GetName(): continue
        if not handle in e.GetName(): continue
        hist_name = e.GetName()
        print(f'[i] found histogram: {hist_name}')
        break
    hist = f.Get(hist_name)
    hist.SetDirectory(0)
    f.Close()
    if not hist:
        print(f'Error: {hist_name} is not a valid histogram')
        return None
    
    return hist

def generateClopperPearsonInterval(num,den):
    confidenceLevel = 0.68
    alpha = 1 - confidenceLevel
    
    lowerLimit = round(ROOT.Math.beta_quantile(alpha/2,num,den-num + 1),4)
    if num==den:
        upperLimit=1
    else:
        upperLimit = round(ROOT.Math.beta_quantile(1-alpha/2,num + 1,den-num),4)
    return lowerLimit,upperLimit

def calc_efficiency_err(num, den):
    if den == 0:
        return 0.0, 0.0, 0.0
    eff = num / den
    
    eff_lo, eff_hi = generateClopperPearsonInterval(num, den)
    eff_lo = np.max([0.0, eff_lo])
    eff_hi = np.min([1.0, eff_hi])
    
    eff_err_lo = eff - eff_lo
    eff_err_hi = eff_hi - eff

    return eff, eff_err_lo, eff_err_hi

def efficiency_from_histo(h_tag, h_probe,  verbose=False):
    h_tag.Sumw2()
    h_probe.Sumw2()
    eff_val, eff_elo, eff_ehi = np.zeros(h_tag.GetNbinsX()), np.zeros(h_tag.GetNbinsX()), np.zeros(h_tag.GetNbinsX())
    x_val, x_elo, x_ehi = np.zeros(h_tag.GetNbinsX()), np.zeros(h_tag.GetNbinsX()), np.zeros(h_tag.GetNbinsX())
    for i in range(1, h_tag.GetNbinsX() + 1):
        # x-axis
        x_val[i-1] = h_tag.GetBinCenter(i)
        x_elo[i-1] = h_tag.GetBinCenter(i) - h_tag.GetBinLowEdge(i)
        x_ehi[i-1] = h_tag.GetBinLowEdge(i+1) - h_tag.GetBinCenter(i)
        # efficiency
        n_tag = h_tag.GetBinContent(i)
        n_probe = h_probe.GetBinContent(i)

        this_eff, this_eff_err_lo, this_eff_err_hi = calc_efficiency_err(n_probe, n_tag)
        eff_val[i-1] = this_eff
        eff_elo[i-1] = this_eff_err_lo
        eff_ehi[i-1] = this_eff_err_hi

        #if n_tag > 0:
        #    eff_lo, eff_hi = generateClopperPearsonInterval(n_probe, n_tag)
        #    eff_hi = np.min([1.0, eff_hi])
        #    
        #    eff_elo[i-1] = eff_val[i-1] - eff_lo
        #    eff_ehi[i-1] = eff_hi - eff_val[i-1]
        
        if (verbose) :print(f'bin {i} x = {x_val[i-1]} : {n_probe} / {n_tag} \t eff = {eff_val[i-1]:.2f} +{eff_ehi[i-1]:.2f} -{eff_elo[i-1]:.2f}')

    # asymmertic errors
    efficiency_G = ROOT.TGraphAsymmErrors(
        len(x_val),
        array.array('d', x_val),
        array.array('d', eff_val),
        array.array('d', x_elo),
        array.array('d', x_ehi),
        array.array('d', eff_elo),
        array.array('d', eff_ehi)
    )
    # histogram
    x_val = x_val - x_elo
    x_val = np.append(x_val, x_val[-1] + x_elo[-1] + x_ehi[-1])
    efficiency_H = ROOT.TH1D('eff', 'eff', len(x_val) -1, array.array('d', x_val))
    for i in range(efficiency_H.GetNbinsX()):
        efficiency_H.SetBinContent(i+1, eff_val[i])
        efficiency_H.SetBinError(i+1, (eff_elo[i]+eff_ehi[i])/2.0)

    return efficiency_G, efficiency_H

def style_efficiency(eff, x_label = '', title = '',color = ROOT.kBlack, marker = 20):

    eff.SetMaximum(1.2)
    eff.SetMinimum(0)
    eff.SetTitle(title)

    eff.SetMarkerStyle(marker)
    eff.SetMarkerColor(color)
    eff.SetLineColor(color)
    eff.SetLineWidth(2)
    eff.SetMarkerSize(1.2)
    # x-axis
    eff.GetXaxis().SetTitle(x_label)
    eff.GetXaxis().SetTitleSize(0.05)
    eff.GetXaxis().SetTitleOffset(0.9)
    eff.GetXaxis().SetLabelSize(0.04)
    # y-axis
    eff.GetYaxis().SetTitle('Efficiency')
    eff.GetYaxis().SetTitleSize(0.05)
    eff.GetYaxis().SetTitleOffset(0.9)
    eff.GetYaxis().SetLabelSize(0.04)
    

    return eff

def style_scale_factor(h, x_label = '', y_label = 'Data/MC', yrange = [0.8,1.2], title = '', color = ROOT.kBlack, marker = None):

    h.SetTitle(title)
    if marker : 
        h.SetMarkerStyle(marker)
        h.SetMarkerColor(color)
        h.SetMarkerSize(1.2)
    h.SetLineColor(color)
    h.SetLineWidth(2)
    # x-axis
    h.GetXaxis().SetTitle(x_label)
    h.GetXaxis().SetTitleSize(0.1)
    #h.GetXaxis().SetTitleOffset(0.9)
    h.GetXaxis().SetLabelSize(0.1)
    # y-axis
    h.GetYaxis().SetTitle(y_label)
    h.GetYaxis().SetTitleSize(0.1)
    h.GetYaxis().SetTitleOffset(0.5)
    h.GetYaxis().SetLabelSize(0.1)
    h.GetYaxis().SetRangeUser(yrange[0], yrange[1])
    h.GetYaxis().SetNdivisions(505)

    return h

def style_histogram(h, x_label = '', y_label = '', title = '', color = ROOT.kBlack, marker = None):

    h.SetTitle(title)
    if marker : 
        h.SetMarkerStyle(marker)
        h.SetMarkerColor(color)
        h.SetMarkerSize(1.2)
    h.SetLineColor(color)
    h.SetLineWidth(2)
    # x-axis
    h.GetXaxis().SetTitle(x_label)
    h.GetXaxis().SetTitleSize(0.05)
    h.GetXaxis().SetTitleOffset(0.9)
    h.GetXaxis().SetLabelSize(0.04)
    # y-axis
    h.GetYaxis().SetTitle(y_label)
    h.GetYaxis().SetTitleSize(0.05)
    h.GetYaxis().SetTitleOffset(0.9)
    h.GetYaxis().SetLabelSize(0.04)

    return h

