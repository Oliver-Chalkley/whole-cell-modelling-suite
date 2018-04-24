#!/bin/bash

# This script was created using Oliver Chalkley's computer_communication_framework library - https://github.com/Oliver-Chalkley/computer_communication_framework.

# This script was automatically created by Oliver Chalkley's whole-cell modelling suite. Please contact on o.chalkley@bristol.ac.uk

# Title: test_submisson
# User: unit, test, unit@test.ac.uk

# Affiliation: Test affiliation.
# Last Updated: 2018-04-23 23:52:11.475837

## Job name
#PBS -N test_submisson

## Resource request
#PBS -l nodes=1:ppn=3,walltime=00:00:10
#PBS -q testq

## Job array request
#PBS -t 1-2

## designate output and error files
#PBS -o /panfs/panasas01/bluegem-flex1/database/wcm_suite/unittest/wcms/out_and_error_files
#PBS -e /panfs/panasas01/bluegem-flex1/database/wcm_suite/unittest/wcms/out_and_error_files

# print some details about the job
echo "The Array ID is: ${PBS_ARRAYID}"
echo Running on host `hostname`
echo Time is `date`
echo Directory is `pwd`
echo PBS job ID is ${PBS_JOBID}
echo This job runs on the following nodes:
echo `cat $PBS_NODEFILE | uniq`

module add languages/python-anaconda-4.2-3.5
source activate wholecell_modelling_suite
master=/panfs/panasas01/emat/oc13378/WholeCell/wc/mg/WholeCell-master

# create output directory
base_outDir=/panfs/panasas01/bluegem-flex1/database/wcm_suite/unittest/wcms/output

# go to master directory
cd ${master}

python unittest_model.py /panfs/panasas01/bluegem-flex1/database/wcm_suite/unittest/wcms/output
master=/panfs/panasas01/emat/oc13378/WholeCell/wc/mg/WholeCell-master

# create output directory
base_outDir=/panfs/panasas01/bluegem-flex1/database/wcm_suite/unittest/wcms/output

# go to master directory
cd ${master}

python unittest_model.py /panfs/panasas01/bluegem-flex1/database/wcm_suite/unittest/wcms/output
