#!/bin/bash

# This script was created using Oliver Chalkley's computer_communication_framework library - https://github.com/Oliver-Chalkley/computer_communication_framework.

# This script was automatically created by Oliver Chalkley's whole-cell modelling suite. Please contact on o.chalkley@bristol.ac.uk

# Title: test_submission
# User: test_forename, test_surname, test_email

# Affiliation: Minimal genome group, Bristol Centre for Complexity Science, BrisSynBio, University of Bristol
# Last Updated: 2018-04-16 15:23:05.085984

## Job name
#PBS -N test_submission

## Resource request
#PBS -l nodes=1:ppn=1,walltime=30:00:00
#PBS -q short

## Job array request
#PBS -t 1-100

## designate output and error files
#PBS -e /test/outfiles
#PBS -o /test/errorfiles

# print some details about the job
echo "The Array ID is: ${PBS_ARRAYID}"
echo Running on host `hostname`
echo Time is `date`
echo Directory is `pwd`
echo PBS job ID is ${PBS_JOBID}
echo This job runs on the following nodes:
echo `cat $PBS_NODEFILE | uniq`

# load required modules
module unload apps/matlab-r2013b
module load apps/matlab-r2013a
echo "Modules loaded:"
module list

# create the master directory variable
master=/test/wcm/master

# create output directory
base_outDir=/test/output

# collect the KO combos
ko_list=/test/ko/codes.txt
ko_dir_names=/test/ko/dir_names.txt

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
    for j in `seq 1 1`
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
