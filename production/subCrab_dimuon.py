#!/usr/bin/env python
"""
This is a small script that does the equivalent of multicrab.
source /cvmfs/cms.cern.ch/common/crab-setup.sh
"""
import os
import yaml
from optparse import OptionParser

import CRABClient
from CRABAPI.RawCommand import crabCommand
from CRABClient.ClientExceptions import ClientException
from http.client import HTTPException #python3
#from CRABClient.UserUtilities import config


_ProductionTag = '_SFtest'
def getOptions():
    """
    Parse and return the arguments provided by the user.
    """
    usage = ("Usage: %prog --crabCmd CMD [--workArea WAD --crabCmdOpts OPTS]"
             "\nThe multicrab command executes 'crab CMD OPTS' for each project directory contained in WAD"
             "\nUse multicrab -h for help")

    parser = OptionParser(usage=usage)

    parser.add_option('-c', '--crabCmd',
                      dest = 'crabCmd',
                      default = '',
                      help = "crab command",
                      metavar = 'CMD')

    parser.add_option('-w', '--workArea',
                      dest = 'workArea',
                      default = '',
                      help = "work area directory (only if CMD != 'submit')",
                      metavar = 'WAD')

    parser.add_option('-o', '--crabCmdOpts',
                      dest = 'crabCmdOpts',
                      default = '',
                      help = "options for crab command CMD",
                      metavar = 'OPTS')
    
    parser.add_option('-i', '--inputDataset',
                      dest = 'inputDataset',
                      default = '',
                      help = "input dataset in .yaml file",)

    (options, arguments) = parser.parse_args()

    if arguments:
        parser.error("Found positional argument(s): %s." % (arguments))
    if not options.crabCmd:
        parser.error("(-c CMD, --crabCmd=CMD) option not provided.")
    if options.crabCmd != 'submit':
        if not options.workArea:
            parser.error("(-w WAR, --workArea=WAR) option not provided.")
        if not os.path.isdir(options.workArea):
            parser.error("'%s' is not a valid directory." % (options.workArea))

    return options


def main():

    options = getOptions()
    
    # The submit command needs special treatment.
    if options.crabCmd == 'submit':
        
        #--------------------------------------------------------
        # This is the base config:
        #--------------------------------------------------------
        from CRABClient.UserUtilities import config
        config = config()
         
        config.General.requestName = None
        config.General.workArea = 'BPHTriggerTuples'
        config.General.transferOutputs = True
        config.General.transferLogs = False

        config.JobType.pluginName = 'Analysis'
        config.JobType.psetName = '../test/mumuRootupler.py'
        config.JobType.allowUndistributedCMSSW = True
        
        config.Data.inputDataset = None
        config.Data.inputDBS = 'global'
        #config.Data.splitting = 'FileBased'
        config.Data.splitting = 'LumiBased'
        config.Data.unitsPerJob = 15
        #config.Data.totalUnits  = 500
        #config.Data.lumiMask = '/eos/user/c/cmsdqm/www/CAF/certification/Collisions24/DCSOnly_JSONS/dailyDCSOnlyJSON/Collisions24_13p6TeV_378981_380403_DCSOnly_TkPx.json'
        #config.Data.runRange = '379765-379769'

        config.Data.outLFNDirBase = '/store/group/phys_bphys/cbasile/'+str(config.General.workArea)
        config.Data.publication = False
        config.Data.outputDatasetTag = None
        #config.Data.ignoreLocality = True

        config.Site.storageSite = 'T2_CH_CERN'
        #config.Site.storageSite = 'T3_CH_CERNBOX'
        
        #--------------------------------------------------------
        # get dataset from yaml file
        with open(options.inputDataset, 'r') as stream:
            try:
                input_config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
            
        common  = input_config['common'] if 'common' in input_config else {}
        samples = input_config['samples']

        # common settings
        globaltag = common['globaltag'] if 'globaltag' in common else ''
        isMC = common['isMC'] if 'isMC' in common else False

        config.JobType.pyCfgParams = [
            f'period=default',
            f'isMC={isMC}',
            f'globalTag={globaltag}',
        ]

        for dataset_name in samples:
            # splitting by files for MC
            if isMC:
                config.Data.splitting = 'FileBased'
                config.Data.unitsPerJob = int(samples[dataset_name]['filesperjob'])
            
            # dataset
            inDS = samples[dataset_name]['dataset']
            print(f'[+] processing {dataset_name} dataset : {inDS} ')
            # inDS is of the form /A/B/C. Since B is unique for each inDS, use this in the CRAB request name.
            requestName = inDS.split('/')[1]+'-'+inDS.split('/')[2] + _ProductionTag
            if len(requestName) > 100:
                tag_len = len(_ProductionTag)
                requestName = (inDS.split('/')[1]+'-'+inDS.split('/')[2])[:100 - tag_len] + _ProductionTag
            config.General.requestName = requestName
            config.Data.inputDataset = inDS
            config.Data.outputDatasetTag = '%s_%s' % (config.General.workArea, config.General.requestName)
            print(config)
            # Submit.
            try:
                print ( "Submitting for input dataset %s" % (inDS) )
                crabCommand(options.crabCmd, config = config, *options.crabCmdOpts.split())
            except HTTPException as hte:
                print ( "Submission for input dataset %s failed: %s" % (inDS, hte.headers) )
            except ClientException as cle:
                print ( "Submission for input dataset %s failed: %s" % (inDS, cle) )

                # All other commands can be simply executed.
    elif options.workArea:

        for dir in os.listdir(options.workArea):
            projDir = os.path.join(options.workArea, dir)
            if not os.path.isdir(projDir):
                continue
            # Execute the crab command.
            msg = "Executing (the equivalent of): crab %s --dir %s %s" % (options.crabCmd, projDir, options.crabCmdOpts)
            print ( "-"*len(msg) )
            print ( msg )
            print ( "-"*len(msg) )
            try:
                crabCommand(options.crabCmd, dir = projDir, *options.crabCmdOpts.split())
            except HTTPException as hte:
                print ( "Failed executing command %s for task %s: %s" % (options.crabCmd, projDir, hte.headers) )
            except ClientException as cle:
                print ( "Failed executing command %s for task %s: %s" % (options.crabCmd, projDir, cle) )


if __name__ == '__main__':
    main()
