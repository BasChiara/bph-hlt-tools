import json
import argparse
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import config as config
import utils as utils

parser = argparse.ArgumentParser(description="Trigger efficiency calculation script")

parser.add_argument('--in_tagtuples', type=str, required=True, help="input tagtuples file(s)")
parser.add_argument('--tnp_selection', type=str, required=True, help="tag and probe selection")

args = parser.parse_args()
# read input tagtuples file
if os.path.exists(args.in_tagtuples):
    with open(args.in_tagtuples) as f:
        input_data = json.load(f)
else:
    print(f"File {args.in_tagtuples} not found")
    sys.exit(1)

print(f'[+] reading files from {args.in_tagtuples}')

inputs          = input_data['dataset']
process         = input_data['process']
run             = input_data['run_era']
tag_path        = input_data.get('tagPath', None)
probe_path      = input_data.get('probePath', None)
label           = input_data['output_label']
isMC            = 'mc' if input_data['isMC'] else 'data'
print(f' --- tag path: {tag_path} ---')
print(f' --- probe path: {probe_path} --- \n')

# read input selection file
if os.path.exists(args.tnp_selection):
    with open(args.tnp_selection) as f:
        selection_data = json.load(f)
else:  
    print(f"[ERROR] selection config file {args.tnp_selection} not found")
    exit(1) 
print(f'[CONF] reading selection from {args.tnp_selection}\n')
selection_name = selection_data['name']
# tag and probe selection -> check if the tag selection is a list or a string
tag_selection   = selection_data['tag_selection']
if isinstance(tag_selection, list):
    tag_selection = ' & '.join(tag_selection)
probe_selection = selection_data['probe_selection']
if isinstance(probe_selection, list):
    probe_selection = ' & '.join(probe_selection)


for era in inputs:

    output_label = f'{label}_{isMC}{era}_{process}'
    command = f'python3 TriggerEfficiency_v1.py --input {inputs[era]} -o {output_label} -r {run}_{selection_name}  -t {tag_path} -p {probe_path} --denQ "{tag_selection}" --numQ "{probe_selection}"'

    os.system(command) 