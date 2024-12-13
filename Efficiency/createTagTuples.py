import pandas as pd
import time
import matplotlib.pyplot as plt
import uproot3 as uproot
import numpy as np
import glob
import ROOT
import os


print('Imports')
def create_dict_from_df_destructive(dataframe, destructive=True):
    dict_df = dict()
    #dataframe.reset_index(inplace=True)
    dataframe = dataframe.reset_index()
    if 'Slice' in dataframe:
        for trg in set(dataframe.Slice):
            print(f'Slice_HLT_{trg}')
            dataframe[f'Slice_HLT_{trg}'] = 0
            dataframe[f'Slice_HLT_{trg}'][dataframe.Slice==trg] = 1
        dataframe.drop('Slice', axis=1, inplace=True)
        
    #pdb.set_trace()
    for var in dataframe:
        if 'bool' in str(dataframe[var].dtype) or 'unit' in str(dataframe[var].dtype): 
            dict_df[var] = np.array(dataframe[var], dtype=np.int8)
        else:
            if 'HLT' in var: dict_df[var] = np.array(dataframe[var], dtype=np.int8)
            if 'L1' in var: dict_df[var] = np.array(dataframe[var], dtype=np.int8)
            if var in ['run', 'lumiblock', 'luminosityBlock', 'event', 'subentry', 'nB', 'nMu', 'nVtx']:
                dict_df[var] = np.array(dataframe[var], dtype=np.int64)
            else: dict_df[var] = np.array(dataframe[var])
        if destructive: dataframe.drop(var, axis=1, inplace=True)
    return dict_df


def save_dict_to_root(dictionary, output_file, tree):
    dict_types = dict()
    for var in dictionary: 
        if 'object' in str(type(dictionary[var].dtype)):
            dictionary[var] = list(dictionary[var])
            dict_types[var] = str
        else: dict_types[var] = dictionary[var].dtype
    uproot_file = uproot.recreate(output_file)
    uproot_file[tree] = uproot.newtree(dict_types)
    uproot_file[tree].extend(dictionary)
    uproot_file.close()
    print(f'File {output_file} saved')


def save_df_to_root(dataframe, output_file, tree):
    dictionary = create_dict_from_df_destructive(dataframe)
    save_dict_to_root(dictionary, output_file, tree)





import argparse

my_parser = argparse.ArgumentParser(prog='Create Tag DataSets',
                                    description='This scripts produces histograms for events that were collected by a given trigger on a given variable',
                                    )
my_parser.add_argument('--tagPath',
                    type = str,
                    default='HLT_DoubleMu4_3_LowMass_SS_v',
                    help='path of the input files')
my_parser.add_argument('--data_path',
                    type = str,
                    default='/eos/user/h/hcrottel/BPHTriggerTuples/ParkingDoubleMuonLowMass3/BPHTriggerTuples_ParkingDoubleMuonLowMass3-Run2024C-PromptReco-v1HLTStudy/*/*/*root',
                    help='path of the input files')
my_parser.add_argument('--name',
                    type = str,
                    default='',
                    help='path of the input files')
my_parser.add_argument('--dryrun',
                    action='store_true',
                    help='Print the commands without running them')

args  = my_parser.parse_args()

print(args)

tagPath=args.tagPath
data_path=args.data_path + '*root'
for indx, k in enumerate(data_path.split('/')):
    print(k)
    if 'BPHTriggerTuples_' in k: break

name = args.name
if args.dryrun:
    dataset='ParkingDoubleMuonLowMass0'
    sample=""
    year="2024I"
    version="v1" 
else:
    dataset=data_path.split('/')[indx-1].replace('*','')
    sample=data_path.split('/')[-2].replace('*','')
    year=data_path.split('/')[indx].split('-')[1]
    version=data_path.split('/')[indx].split('-')[-1]
data_name=f'{name+"_" if name else ""}{dataset}_{year}_{version}_{tagPath}{"_"+sample if sample else ""}'
print(data_name)

bad_files = []

#files = glob.glob('/eos/user/h/hcrottel/BPHTriggerTuples/Muon*/BPHTriggerTuples_Muon*-Run2023D-PromptReco-v2HLTStudy/*/0000/*root')
files = glob.glob(data_path)
#if len(files) > 100: files = files[:100]
print('Total files: ', len(files))
output_file = f'/eos/user/c/cbasile/BPH_trigger/CMSSW_14_0_5/src/myAnalyzers/bph-hlt-tools/Efficiency/{data_name}.root'
main_path = f'/eos/user/c/cbasile/BPH_trigger/TagTuples/Run3_MC/'
os.makedirs(main_path, exist_ok=True)
output_file = f'{main_path}{data_name}.root'
time.sleep(5)

dataTag = list()
for indx, fn in enumerate(files):
    print(fn, end='')
    try:
        ROOT.TFile(fn)
        print('\n')        
    except OSError:
        bad_files.append(fn)
        print('Bad file')
        continue
    #if fn in bad_files: continue
    #if indx>10: break
    file = uproot.open(fn)
    data = file['rootuple']['ntuple'].arrays(outputtype=pd.DataFrame)
    file.close()
    
    print('[+] data Loaded')
    muonFiringTag = data.filter(regex=f'mu.*{tagPath}').sum(axis=1)>0 # mask : at least one muon fired the tagHLT
    dataTag_ = data.loc[muonFiringTag]
    #dataTag_.set_index('event', inplace=True)

    # rename 'mu1' -> muTag, 'mu2' -> muProbe 
    dataTag_leadingTag  = (dataTag_.loc[dataTag_[f'mu1_{tagPath}']==1]).copy()
    dataTag_leadingTag.rename(mapper=lambda x: x.replace('mu1', 'muTag'), axis=1, inplace=True)
    dataTag_leadingTag.rename(mapper=lambda x: x.replace('mu2', 'muProbe'), axis=1, inplace=True)
    dataTag_leadingTag.rename(mapper=lambda x: x.replace('muon1', 'muTag'), axis=1, inplace=True)
    dataTag_leadingTag.rename(mapper=lambda x: x.replace('muon2', 'muProbe'), axis=1, inplace=True)
    # rename 'mu1' -> muTag, 'mu2' -> muProbe
    dataTag_trailingTag = (dataTag_[dataTag_[f'mu2_{tagPath}']==1]).copy()
    dataTag_trailingTag.rename(mapper=lambda x: x.replace('mu2', 'muTag'), axis=1, inplace=True)
    dataTag_trailingTag.rename(mapper=lambda x: x.replace('mu1', 'muProbe'), axis=1, inplace=True)
    dataTag_trailingTag.rename(mapper=lambda x: x.replace('muon2', 'muTag'), axis=1, inplace=True)
    dataTag_trailingTag.rename(mapper=lambda x: x.replace('muon1', 'muProbe'), axis=1, inplace=True)    

    # concatenate the two datasets
    _dataTag = pd.concat([dataTag_leadingTag, dataTag_trailingTag])
    
    dataTag.append(_dataTag)

dataTag = pd.concat(dataTag)
lxySig = dataTag['lxy'] / dataTag['lxyerr']
dataTag = pd.concat([dataTag, lxySig.rename('lxySig')], axis=1)
save_df_to_root(dataTag, output_file, tagPath)

print('Total Bad Files: ', len(bad_files))
