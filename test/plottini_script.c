{
ntuple->Scan("event:L1_mu1_pt:DiMu_mu1_pt:mu1_L1prop_dR:L1_mu2_pt:DiMu_mu2_pt:mu2_L1prop_dR:DiMu_mass:DiMu_L1_dR", selection)

ntuple->Draw("(L1_mu1_pt-mu1_pt)/mu1_pt>>h_tagpt_diff(60, -1, 4)", selection);
h_tagpt_diff->SetLineWidth(2);
h_tagpt_diff->SetLineColor(kBlue);
h_tagpt_diff->GetXaxis()->SetTitle("(L1_mu1_pt-mu1_pt)/mu1_pt");
h_tagpt_diff->GetYaxis()->SetTitle("Events");
h_tagpt_diff->Draw();

ntuple->Draw("(L1_mu2_pt-mu2_pt)/mu2_pt>>h_probept_diff(60, -1, 4)", selection);
h_probept_diff->SetLineWidth(2);
h_probept_diff->SetLineColor(kRed);
h_probept_diff->GetXaxis()->SetTitle("(L1_mu2_pt-mu2_pt)/mu2_pt");
h_probept_diff->GetYaxis()->SetTitle("Events");
h_probept_diff->Draw("same");

ntuple->Draw("DiMu_L1_dR>>h_l1dR(41, -0.05, 2.0)", selection);
h_l1dR->SetLineColor(kRed);
h_l1dR->SetFillColor(kRed);
h_l1dR->SetFillStyle(3004);
h_l1dR->SetTitle("");
h_l1dR->SetLineWidth(3);
h_l1dR->Draw();
}
//TString selection = "(DiMu_mass>2.9) & (DiMu_mass<3.3) & (DiMu_Prob > 0.005) & (DiMu_mu1_pt>8)&(mu1Global==1)&(mu1loose==1)&(mu2loose==1)&(mu1_HLT_Mu8_v ==1)";