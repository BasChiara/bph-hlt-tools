import htcondor
col = htcondor.Collector()
credd = htcondor.Credd()
credd.add_user_cred(htcondor.CredTypes.Kerberos, None)
import classad
import os

# Define the EOS path to your working directory
eos_path = os.path.expandvars("$EOS")
proxy_path = os.path.expandvars("$HOME/X509_USER_PROXY")
# Define the list of input files required for the job
input_files = [
    proxy_path,
    "../utils.py",
    "../config.py",
    "../cutNcount_efficiency.py",
    "../data/tagtuples_HLT_Mu8_v_MC_Jpsito2Mu_pythia8_2022EE_v4.json",
    "../selection/mediumID_selection_L1.json",
    "wrapper.sh"
]

# Create the Submit object with job specifications
submit_description = htcondor.Submit({
    "executable": "wrapper.sh",
    "arguments": "",
    "x509userproxy"     : proxy_path,
    "use_x509userproxy" : "True",
    "should_transfer_files": "YES",
    "when_to_transfer_output": "ON_EXIT",
    "transfer_output_files": "condor_test/, job.out, job.err, job.log",
    "output_destination": "root://eosuser.cern.ch//eos/user/c/cbasile/HLT_DoubleMu/CMSSW_14_0_5/src/myAnalyzers/bph-hlt-tools/Efficiency_v2/results2022_v4/",
    "transfer_input_files": ", ".join(input_files),
    "output": "job.out",
    "error": "job.err",
    "log": "job.log",
    "request_cpus": "1",
    "request_memory": "1GB",
    "request_disk": "1GB",
    "getenv": "True"
})

with open("job.sub", "w") as f:
    f.write(str(submit_description))
exit()

# Connect to the local schedd
schedd = htcondor.Schedd()

# 1) Submit with spooling hold
ads = []
submit_result = schedd.submit(
    submit_description,
    spool=True,
    ad_results=ads
)
print(f"Cluster {submit_result.cluster()} submitted, held for spooling")

# 2) Perform the actual spooling transfer
schedd.spool(ads)
print("Input files spooled; jobs now released for execution")
