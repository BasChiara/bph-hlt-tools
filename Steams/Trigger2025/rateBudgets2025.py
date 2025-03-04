#!/usr/bin/env python3
from scipy.integrate import quad

# slope of luminosity decay [Hz/cm2 / hours]
lumi_slope = (1.82 - 2.02) / (200 * 23.31 / 3600 )

# number of lumi-levelling hours
lumilevel_hours = 6

# peak instantaneous luminosity [E34 Hz/cm2]
peak_lumi = 2.1

# peak L1T rate pre-deadtime [kHz]
peak_l1tr = 110.

# deadtime [%]
deadtime = 0.04

# Bare rate of L1_SingleMu5_SQ14_BMTF at 2.1E34 Hz/cm2 [kHz]
l1t_mu5_peak_rate = 52

# single-muon parking: relative increase wrt 2024 (35% for looser IP cut)
park_m1sfac = 1.35

# conversion factor from rate of L1_SingleMu5_SQ14_BMTF to rate of HLT_Mu0_Barrel_L1HP5_IP4_v
# (based on 150 Hz HLT estimated for 0.5 kHz of L1T rate, see Trigger Reviews)
hltfrac_m1 = 0.30

# RAW event size post-repacking at PU ~64 [MB/event]
peak_evtsize = 1.05

# HLT rate of sum(prompt) at peak lumi [kHz]
peak_hlt_prompt = 3.0

# HLT rate of single-muon parking at peak lumi [kHz]
peak_hlt_m1 = 1.4 * park_m1sfac

# HLT rate of sum(parking) at peak lumi [kHz]
# 3.00 kHz corresponds to the 2024 parking rate without single-muon triggers
# 0.25 kHz accounts for extra rate expected from the ParkingLLP PD(s)
peak_hlt_parkin = 3.0 + 0.25 + peak_hlt_m1

# instantaneous luminosity as function of time [Hz/cm2]
def lumi(time_hours):
    return min(peak_lumi, peak_lumi + lumi_slope * (time_hours - lumilevel_hours))

# ratio of instantaneous luminosity to peak instantaneous luminosity
def lumi_factor(time_hours):
    return lumi(time_hours) / peak_lumi

# L1T rate of the "2p0E34" PS column as function of time [kHz]
def l1t_rate(time_hours):
    return peak_l1tr * lumi_factor(time_hours)

# Extra rate from L1_SingleMu5_SQ14_BMTF [kHz].
# Corresponds to the lowest of two values.
#   1. The spare L1T rate available during luminosity decay.
#   2. The unprescaled rate of L1_SingleMu5_SQ14_BMTF (ignoring overlaps).
def l1t_mu5_extra_rate(time_hours):
    return max(0, min(l1t_mu5_peak_rate * lumi(time_hours) / peak_lumi, peak_l1tr - l1t_rate(time_hours)))

# HLT prompt rate as function of time [kHz]
def hlt_rate_prompt(time_hours):
    return peak_hlt_prompt * lumi_factor(time_hours)

# HLT parking rate as function of time [kHz]
# Assumptions.
#  - All the "spare" L1T rate comes from L1_SingleMu5_SQ14_BMTF,
#    and translates to "times hltfrac_m1" extra HLT rate.
#  - The rate of all Parking streams goes down with luminosity
#    (not true for ParkingDoubleMuonLowMass, but the effect is not large).
#  - The L1T rate is maximised at all times as if there were infinite prescale (PS) columns;
#    this is conservative, given the limited number of PS columns used in reality.
def hlt_rate_parkin(time_hours):
    lumi_fac = lumi_factor(time_hours)
    return peak_hlt_parkin * lumi_fac + hltfrac_m1 * (1 - deadtime) * l1t_mu5_extra_rate(time_hours)

# RAW event size post-repacking as function of time [MB/event]
def event_size(time_hours):
    return peak_evtsize * lumi_factor(time_hours)

# HLT prompt bandwidth as function of time [GB/s]
def hlt_band_prompt(time_hours):
    return hlt_rate_prompt(time_hours) * event_size(time_hours)

# HLT parking bandwidth as function of time [GB/s]
def hlt_band_parkin(time_hours):
    return hlt_rate_parkin(time_hours) * event_size(time_hours)

# Per-fill average of a certain quantity (e.g. hlt_band_parkin) as function of the fill duration in hours
def perfill_avg(func, time_hours):
    return quad(func, 0, time_hours)[0] / time_hours

if __name__ == '__main__':
    print('-'*100)

    # Scenario #1
    #  - Luminosity levelling + 6h of luminosity decay
    lumidecay_hours_scenario1 = 6
    fill_total_hours_scenario1 = lumilevel_hours + lumidecay_hours_scenario1
    hlt_band_prompt_avg_scenario1 = perfill_avg(hlt_band_prompt, fill_total_hours_scenario1)
    hlt_band_parkin_avg_scenario1 = perfill_avg(hlt_band_parkin, fill_total_hours_scenario1)
    print(f'Scenario #1: {lumilevel_hours}h leveling, {lumidecay_hours_scenario1}h decay')
    print(f' - Per-fill average bandwidth [GB/s]')
    print(f'   - Prompt  {hlt_band_prompt_avg_scenario1:>4.2f}')
    print(f'   - Parking {hlt_band_parkin_avg_scenario1:>4.2f}')
    print('-'*100)

    # Scenario #2
    #  - Only luminosity levelling.
    #  - Number of hours does not matter here (peak == average)
    lumidecay_hours_scenario2 = 0
    fill_total_hours_scenario2 = lumilevel_hours + lumidecay_hours_scenario2
    hlt_band_prompt_avg_scenario2 = perfill_avg(hlt_band_prompt, fill_total_hours_scenario2)
    hlt_band_parkin_avg_scenario2 = perfill_avg(hlt_band_parkin, fill_total_hours_scenario2)
    print(f'Scenario #2: {lumilevel_hours}h leveling, {lumidecay_hours_scenario2}h decay')
    print(f' - Per-fill average bandwidth [GB/s]')
    print(f'   - Prompt  {hlt_band_prompt_avg_scenario2:>4.2f}')
    print(f'   - Parking {hlt_band_parkin_avg_scenario2:>4.2f}')
    print('-'*100)