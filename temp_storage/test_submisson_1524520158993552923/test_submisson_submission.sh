#!/bin/bash

# This script was created using Oliver Chalkley's computer_communication_framework library - https://github.com/Oliver-Chalkley/computer_communication_framework.

# This script was automatically created by Oliver Chalkley's whole-cell modelling suite. Please contact on o.chalkley@bristol.ac.uk

# Title: test_submisson
# User: unit, test, unit@test.ac.uk

# Affiliation: Test affiliation.
# Last Updated: 2018-04-23 22:49:19.002194

## Job name
#PBS -N test_submisson

## Resource request
#PBS -l nodes=1:ppn=3,walltime=30:00:00
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

# load required modules
module load apps/matlab-r2013a
echo "Modules loaded:"
module list

# create the master directory variable
master=/panfs/panasas01/emat/oc13378/WholeCell/wc/mg/WholeCell-master

# create output directory
base_outDir=/panfs/panasas01/bluegem-flex1/database/wcm_suite/unittest/wcms/output

# collect the KO combos
ko_list=/panfs/panasas01/bluegem-flex1/database/wcm_suite/unittest/wcms/runfiles/ko_sets.list
ko_dir_names=/panfs/panasas01/bluegem-flex1/database/wcm_suite/unittest/wcms/runfiles/ko_set_names.list

# Get all the gene KOs and output folder names
for i in `seq 1 1`
do
    Gene[${i}]=$(awk NR==$((1*(${PBS_ARRAYID}-1)+${i})) ${ko_list})
    unique_ko_dir_name[${i}]=$(awk NR==$((1*(${PBS_ARRAYID}-1)+${i})) ${ko_dir_names})
done

# go to master directory
cd ${master}

# NB have limited MATLAB to a single thread
options="-nodesktop -noFigureWindows -nosplash -singleCompThread"

# run 16 simulations in parallel
echo "Running simulations (single threaded) in parallel - let's start the timer!"
start=`date +%s`

# create all the directories for the diarys (the normal output will be all mixed up cause it's in parrallel!)
for i in `seq 1 1`
do
    for j in `seq 1 3`
    do
        specific_ko="$(echo ${Gene[${i}]} | sed 's/{//g' | sed 's/}//g' | sed "s/'//g" | sed 's/"//g' | sed 's/,/-/g')/${j}"
        mkdir -p ${base_outDir}/${unique_ko_dir_name[${i}]}/diary${j}
        matlab ${options} -r "diary('${base_outDir}/${unique_ko_dir_name[${i}]}/diary${j}/diary.out');addpath('${master}');setWarnings();setPath();runSimulation('runner','koRunner','logToDisk',true,'outDir','${base_outDir}/${unique_ko_dir_name[${i}]}/${j}','jobNumber',$((no_of_repetitions_of_each_ko*no_of_unique_ko_sets_per_array_job*(${PBS_ARRAYID}-1)+no_of_unique_ko_sets_per_array_job*(${i}-1)+${j})),'koList',{{${Gene[${i}]}}});diary off;exit;" &
    done
done
wait

end=`date +%s`
runtime=$((end-start))
echo "$((${no_of_unique_ko_sets_per_array_job}*${no_of_repetitions_of_each_ko})) simulations took: ${runtime} seconds."
