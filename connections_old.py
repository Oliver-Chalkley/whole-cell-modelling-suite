from base_connection import Connection
import subprocess
import os
import re
import datetime
import pandas as pd
class Bc3(Connection):
	def __init__(self, cluster_user_name, ssh_config_alias, path_to_key, forename_of_user, surname_of_user, user_email, base_output_path = '/panfs/panasas01/emat/oc13378/WholeCell/output', base_runfiles_path = '/panfs/panasas01/emat/oc13378/WholeCell/wc/mg/bc3/runFiles', wholecell_model_master_dir = '/panfs/panasas01/emat/oc13378/WholeCell/wc/mg/WholeCell-master'):
		Connection.__init__(self, cluster_user_name, ssh_config_alias, path_to_key, forename_of_user, surname_of_user, user_email)
		self.submit_command = 'qsub'
		self.information_about_cluster = 'BlueCrystal Phase 3: Advanced Computing Research Centre, University of Bristol.'
		self.base_output_path = base_output_path
		self.base_runfiles_path = base_runfiles_path
		self.wholecell_model_master_dir = wholecell_model_master_dir
		self.activate_venv_list = ['module add languages/python-anaconda-4.2-3.5', 'source activate wholecell_modelling_suite']
		self.path_to_flex1 = '/panfs/panasas01/bluegem-flex1'
		self.path_to_database_dir = self.path_to_flex1
		self.db_connection = self

	#instance methhods
#	def transferFile(self, source, destination, rsync_flags = "-aP"):
#		super(bc3, self).transferFile(source, destination, rsync_flags)
#
#		return

	def getGeneInfo(self, tuple_of_genes):
		raw_out = self.useStaticDbFunction([tuple_of_genes], 'CodeToInfo')
		if raw_out[0] == 0:
			as_list = eval(raw_out[1].strip().decode('ascii'))
			list_of_column_names = ['code', 'type', 'name', 'symbol', 'functional_unit', 'deletion_phenotype', 'essential_in_model', 'essential_in_experiment']
			dict_out = {list_of_column_names[name_idx]: [as_list[element_idx][name_idx] for element_idx in range(len(as_list))] for name_idx in range(len(list_of_column_names))}
		else:
			raise ValueError("Failed to retrieve sql data. Query returned: ", raw_out)

		return dict_out

	def useStaticDbFunction(self, list_of_function_inputs, function_call, path_to_staticDb_stuff='/panfs/panasas01/bluegem-flex1/database/staticDB'):
		"""Takes a tuple of gene codes and return info about the genes"""
		add_anoconda_module = 'module add languages/python-anaconda-4.2-3.5'
		activate_virtual_environment = 'source activate wholecell_modelling_suite'
		change_to_lib_dir = 'cd ' + path_to_staticDb_stuff
		get_data = 'python -c "from staticDB import io as sio;static_db_conn = sio();print(static_db_conn.' + function_call + '(' + ','.join(map(str, list_of_function_inputs)) + '))"'
		cmd = "ssh " + self.ssh_config_alias + ";" + add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_data
		cmd_list = ["ssh", self.ssh_config_alias, add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_data]
		raw_out = Connection.getOutput(cmd_list)

		return raw_out


	def sendSqlToStaticDb(self, sql_command, path_to_staticDb_stuff='/panfs/panasas01/bluegem-flex1/database/staticDB'):
		"""Takes an SQLITE3 command as a string and sends it to static.db and returns it the output."""
		add_anoconda_module = 'module add languages/python-anaconda-4.2-3.5'
		activate_virtual_environment = 'source activate wholecell_modelling_suite'
		change_to_lib_dir = 'cd ' + path_to_staticDb_stuff
		get_data = 'python -c "from staticDB import io as sio;static_db_conn = sio();print(static_db_conn.raw_sql_query(\'' + sql_command + '\'))"'
		cmd = "ssh " + self.ssh_config_alias + ";" + add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_data
		cmd_list = ["ssh", self.ssh_config_alias, add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_data]
		raw_out = Connection.getOutput(cmd_list)

		return raw_out

	def convertGeneCodeToId(self, tuple_of_gene_codes, path_to_staticDb_stuff='/panfs/panasas01/bluegem-flex1/database/staticDB'):
		"""Takes a tuple of genes code and returns a tuple of corresponding gene IDs."""
		if type(tuple_of_gene_codes) is not tuple:
			raise TypeException('Gene codes must be a tuple (even if only 1! i.e. single_tuple = (\'MG_001\',)) here type(tuple_of_gene_codes)=', type(tuple_of_gene_codes))
		add_anoconda_module = 'module add languages/python-anaconda-4.2-3.5'
		activate_virtual_environment = 'source activate wholecell_modelling_suite'
		change_to_lib_dir = 'cd ' + path_to_staticDb_stuff
		get_gene_id = 'python -c "from staticDB import io as sio;static_db_conn = sio();print(static_db_conn.CodeToId(' + str(tuple_of_gene_codes) + '))"'
		cmd = "ssh " + self.ssh_config_alias + ";" + add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_gene_id
		cmd_list = ["ssh", self.ssh_config_alias, add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_gene_id]
		raw_out = Connection.getOutput(cmd_list)

		# send command and get output
		output = raw_out
		output[1] = eval(str(output[1], "utf-8").rstrip())
		# it doesn't output the answer in the order you input it so we need to make a dictionary
		codeToId_dict = {}
		for out in output[1]:
			codeToId_dict[out[1]] = out[0]

		return codeToId_dict

	def checkQueue(self, job_number='NONE'):
		"""This function takes a job number and returns a list of all the array numbers of that job still running."""
		if job_number == 'NONE':
			print("Warning: No job number given!")
		grep_part_of_cmd = "qstat -tu " + self.user_name + " | grep \'" + str(job_number) + "\' | awk \'{print $1}\' | awk -F \"[][]\" \'{print $2}\'"

#		cmd = ["ssh", self.ssh_config_alias, grep_part_of_cmd]
		output_dict = self.sendCommand([grep_part_of_cmd])

		return output_dict

	def checkDiskUsage(self):
		"""This function returns disk usage details."""
		# create all the post connection commands needed
		get_disk_usage_units_command = "pan_quota | awk \'{print $1}\' | tail -n 2 | head -n 1 | sed \'s/[<>]//g\'"
		get_disk_usage_command = "pan_quota | awk \'{print $1}\' | tail -n 1"
		get_disk_usage_soft_limit_command = "pan_quota | awk \'{print $2}\' | tail -n 1"
		get_disk_usage_hard_limit_command = "pan_quota | awk \'{print $3}\' | tail -n 1"
		# combine the connection command with the post connection commands in a list (as is recomended).
		units_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_units_command]
		usage_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_command]
		soft_limit_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_soft_limit_command]
		hard_limit_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_hard_limit_command]
		# send the commands and save the exit codes and outputs
		units = Connection.getOutput(units_cmd)
		usage = Connection.getOutput(usage_cmd)
		soft_limit = Connection.getOutput(soft_limit_cmd)
		hard_limit = Connection.getOutput(hard_limit_cmd)
		# convert string outputs to floats where neccessary
		units[1] = str(units[1], "utf-8").rstrip()
		usage[1] = float(usage[1])
		soft_limit[1] = float(soft_limit[1])
		hard_limit[1] = float(hard_limit[1])
		# print some stats
		print(100 * (usage[1] / (1.0 * hard_limit[1]) ),"% of total disk space used.\n\n",hard_limit[1] - usage[1]," ",units[1]," left until hard limit.\n\n",soft_limit[1] - usage[1]," ",units[1]," left unit soft limit.", sep='')
		
		return usage, soft_limit, hard_limit, units

	def createStandardKoSubmissionScript(self, output_filename, pbs_job_name, no_of_unique_kos, path_and_name_of_unique_ko_dir_names, no_of_repetitions_of_each_ko, wholecell_model_master_dir, output_dir, path_and_name_of_ko_codes, outfile_name_and_path, errorfile_name_and_path):
		import subprocess
		# this shouldn't change but gonna leave it there just in case
		queue_name = 'short'
		# set job array numbers to None so that we can check stuff has wprked later
		job_array_numbers = None
		# The maximum job array size on BC3
		max_job_array_size = 500
		# initialise output dict
		output_dict = {}
		# test that a reasonable amount of jobs has been submitted (This is not a hard and fast rule but there has to be a max and my intuition suggestss that it will start to get complicated around this level i.e. queueing and harddisk space etc)
		total_sims = no_of_unique_kos * no_of_repetitions_of_each_ko
		if total_sims > 20000:
			raise ValueError('Total amount of simulations for one batch submission must be less than 20,000, here total_sims=',total_sims)

		output_dict['total_sims'] = total_sims
		# spread simulations across array jobs
		if no_of_unique_kos <= max_job_array_size:
			no_of_unique_kos_per_array_job = 1
			no_of_arrays = no_of_unique_kos
			job_array_numbers = '1-' + str(no_of_unique_kos)
			walltime = '30:00:00'
		else:
			# job_array_size * no_of_unique_kos_per_array_job = no_of_unique_kos so all the factors of no_of_unique_kos is
			common_factors = [x for x in range(1, no_of_unique_kos+1) if no_of_unique_kos % x == 0]
			# make the job_array_size as large as possible such that it is less than max_job_array_size
			factor_idx = len(common_factors) - 1
			while factor_idx >= 0:
				if common_factors[factor_idx] < max_job_array_size:
					job_array_numbers = '1-' + str(common_factors[factor_idx])
					no_of_arrays = common_factors[factor_idx]
					no_of_unique_kos_per_array_job = common_factors[(len(common_factors)-1) - factor_idx]
					factor_idx = -1
				else:
					factor_idx -= 1

			# raise error if no suitable factors found!
			if job_array_numbers is None:
				raise ValueError('job_array_numbers should have been assigned by now! This suggests that it wasn\'t possible for my algorithm to split the KOs across the job array properly. Here no_of_unique_kos=', no_of_unique_kos, ' and the common factors of this number are:', common_factors)

			# add some time to the walltime because I don't think the jobs have to startat the same time
			walltime = '35:00:00'

		output_dict['no_of_arrays'] = no_of_arrays
		output_dict['no_of_unique_kos_per_array_job'] = no_of_unique_kos_per_array_job
		output_dict['no_of_repetitions_of_each_ko'] = no_of_repetitions_of_each_ko
		# calculate the amount of cores per array job - NOTE: for simplification we only use cores and not nodes (this is generally the fastest way to get through the queue anyway)
		no_of_cores = no_of_repetitions_of_each_ko * no_of_unique_kos_per_array_job
		output_dict['no_of_sims_per_array_job'] = no_of_cores
		output_dict['list_of_rep_dir_names'] = list(range(1, no_of_repetitions_of_each_ko + 1))
		no_of_nodes = 1
		# write the script to file
		with open(output_filename, mode='wt', encoding='utf-8') as myfile:
			myfile.write("#!/bin/bash" + "\n")
			myfile.write("\n")
			myfile.write("# This script was automatically created by Oliver Chalkley's whole-cell modelling suite. Please contact on o.chalkley@bristol.ac.uk" + "\n")
			myfile.write("# Title: " + pbs_job_name + "\n")
			myfile.write("# User: " + self.forename_of_user + ", " + self.surename_of_user + ", " + self.user_email + "\n")
			myfile.write("# Affiliation: Minimal Genome Group, Life Sciences, University of Bristol " + "\n")
			myfile.write("# Last Updated: " + str(datetime.datetime.now()) + "\n")
			myfile.write("\n")
			myfile.write("# BC3: 223 base blades which have 16 x 2.6 GHz SandyBridge cores, 4GB/core and a 1TB SATA disk." + "\n")
			myfile.write("\n")
			myfile.write("## Job name" + "\n")
			myfile.write("#PBS -N " + pbs_job_name + "\n")
			myfile.write("\n")
			myfile.write("## Resource request" + "\n")
			myfile.write("#PBS -l nodes=" + str(no_of_nodes) + ":ppn=" + str(no_of_cores) + ",walltime=" + walltime + "\n")
			myfile.write("#PBS -q " + queue_name + "\n")
			myfile.write("\n")
			myfile.write("## Job array request" + "\n")
			myfile.write("#PBS -t " + job_array_numbers + "\n")
			myfile.write("\n")
			myfile.write("## designate output and error files" + "\n")
			myfile.write("#PBS -e " + outfile_name_and_path + "\n")
			myfile.write("#PBS -o " + errorfile_name_and_path + "\n")
			myfile.write("\n")
			myfile.write("# print some details about the job" + "\n")
			myfile.write('echo "The Array ID is: ${PBS_ARRAYID}"' + "\n")
			myfile.write('echo Running on host `hostname`' + "\n")
			myfile.write('echo Time is `date`' + "\n")
			myfile.write('echo Directory is `pwd`' + "\n")
			myfile.write('echo PBS job ID is ${PBS_JOBID}' + "\n")
			myfile.write('echo This job runs on the following nodes:' + "\n")
			myfile.write('echo `cat $PBS_NODEFILE | uniq`' + "\n")
			myfile.write("\n")
			myfile.write("# load required modules" + "\n")
			myfile.write("module unload apps/matlab-r2013b" + "\n")
			myfile.write("module load apps/matlab-r2013a" + "\n")
			myfile.write('echo "Modules loaded:"' + "\n")
			myfile.write("module list" + "\n")
			myfile.write("\n")
			myfile.write("# create the master directory variable" + "\n")
			myfile.write("master=" + wholecell_model_master_dir + "\n")
			myfile.write("\n")
			myfile.write("# create output directory" + "\n")
			myfile.write("base_outDir=" + output_dir + "\n")
			myfile.write("\n")
			myfile.write("# collect the KO combos" + "\n")
			myfile.write("ko_list=" + path_and_name_of_ko_codes + "\n")
			myfile.write("ko_dir_names=" + path_and_name_of_unique_ko_dir_names + "\n")
			myfile.write("\n")
			myfile.write("# Get all the gene KOs and output folder names" + "\n")
			myfile.write('for i in `seq 1 ' + str(no_of_unique_kos_per_array_job) + '`' + "\n")
			myfile.write('do' + "\n")
			myfile.write('    Gene[${i}]=$(awk NR==$((' + str(no_of_unique_kos_per_array_job) + '*(${PBS_ARRAYID}-1)+${i})) ${ko_list})' + "\n")
			myfile.write('    unique_ko_dir_name[${i}]=$(awk NR==$((' + str(no_of_unique_kos_per_array_job) + '*(${PBS_ARRAYID}-1)+${i})) ${ko_dir_names})' + "\n")
			myfile.write("done" + "\n")
			myfile.write("\n")
			myfile.write("# go to master directory" + "\n")
			myfile.write("cd ${master}" + "\n")
			myfile.write("\n")
			myfile.write("# NB have limited MATLAB to a single thread" + "\n")
			myfile.write('options="-nodesktop -noFigureWindows -nosplash -singleCompThread"' + "\n")
			myfile.write("\n")
			myfile.write("# run 16 simulations in parallel")
			myfile.write('echo "Running simulations (single threaded) in parallel - let\'s start the timer!"' + "\n")
			myfile.write('start=`date +%s`' + "\n")
			myfile.write("\n")
			myfile.write("# create all the directories for the diarys (the normal output will be all mixed up cause it's in parrallel!)" + "\n")
			myfile.write('for i in `seq 1 ' + str(no_of_unique_kos_per_array_job) + '`' + "\n")
			myfile.write("do" + "\n")
			myfile.write('    for j in `seq 1 ' + str(no_of_repetitions_of_each_ko) + '`' + "\n")
			myfile.write("    do" + "\n")
			myfile.write('        specific_ko="$(echo ${Gene[${i}]} | sed \'s/{//g\' | sed \'s/}//g\' | sed \"s/\'//g\" | sed \'s/\"//g\' | sed \'s/,/-/g\')/${j}"' + "\n")
			myfile.write('        mkdir -p ${base_outDir}/${unique_ko_dir_name[${i}]}/diary${j}' + "\n")
			myfile.write('        matlab ${options} -r "diary(\'${base_outDir}/${unique_ko_dir_name[${i}]}/diary${j}/diary.out\');addpath(\'${master}\');setWarnings();setPath();runSimulation(\'runner\',\'koRunner\',\'logToDisk\',true,\'outDir\',\'${base_outDir}/${unique_ko_dir_name[${i}]}/${j}\',\'jobNumber\',$((no_of_repetitions_of_each_ko*no_of_unique_kos_per_array_job*(${PBS_ARRAYID}-1)+no_of_unique_kos_per_array_job*(${i}-1)+${j})),\'koList\',{{${Gene[${i}]}}});diary off;exit;" &' + "\n")
			myfile.write("    done" + "\n")
			myfile.write("done" + "\n")
			myfile.write("wait" + "\n")
			myfile.write("\n")
			myfile.write("end=`date +%s`" + "\n")
			myfile.write("runtime=$((end-start))" + "\n")
			myfile.write('echo "$((${no_of_unique_kos_per_array_job}*${no_of_repetitions_of_each_ko})) simulations took: ${runtime} seconds."')

		# give the file execute permissions
		subprocess.check_call(["chmod", "700", str(output_filename)])

		return output_dict

	def getJobIdFromSubStdOut(self, stdout):
		return int(re.search(r'\d+', stdout).group())

class Bg(Connection):
	def __init__(self, cluster_user_name, ssh_config_alias, path_to_key, forename_of_user, surname_of_user, user_email, base_output_path = '/projects/flex1/database/wcm_suite/output', base_runfiles_path = '/projects/flex1/database/wcm_suite/runFiles', wholecell_model_master_dir = '/panfs/panasas01/emat/oc13378/WholeCell/wc/mg/WholeCell-master'):
		Connection.__init__(self, cluster_user_name, ssh_config_alias, path_to_key, forename_of_user, surname_of_user, user_email)
		self.submit_command = 'sbatch'
		self.information_about_cluster = 'BlueGem: BrisSynBio, University of Bristol.'
		self.base_output_path = base_output_path
		self.base_runfiles_path = base_runfiles_path
		self.wholecell_model_master_dir = wholecell_model_master_dir
		self.activate_venv_list = ['module add apps/anaconda3-2.3.0', 'source activate whole_cell_modelling_suite']
		self.path_to_flex1 = '/projects/flex1'
		self.path_to_database_dir = self.path_to_flex1
		self.db_connection = self

	#instance methhods
#	def transferFile(self, source, destination, rsync_flags = "-aP"):
#		super(bc3, self).transferFile(source, destination, rsync_flags)
#
#		return

    # TAKEN FROM BASE_CONNECTION SO NEED TO CHECK IT WORKS AND CHANGE THE NAME TO SATISFY THE NEW "CREATEFILELOCALLY" ABSTRACT METHOD
    # MAYBE CREATE A INTERMEDIATE CLASS SINCE THIS FUNCTION WILL ALWAYS BE THE SAME FOR ALL THE WHOLE-CELL MODELL STUFF -THIS WILL AVOID HAVING TO WRITE IT EVERY TIME AND CREATE A CLASS TO EASILY ADD OTHER REPEATING THINGS.
    def convertKosAndNamesToFile(self, ko_code_dict, ko_code_file_path_and_name, ko_dir_name_file_path_and_name):
        """Takes a python dict of gene codes and saves them in a specified path and file name."""
        # check that ko_code_dict has type "dict"
        if type(ko_code_dict) is not dict:
            raise TypeError("ko_code_dict must be a Python dict but here type(ko_code_dict)=%s" %(type(ko_code_dict)))

        # make sure paths exist and if not create them
        # take the file name off the end of both files
        # ko code path
        ko_code_path, ko_code_file = os.path.split(ko_code_file_path_and_name)
        # ko name path
        ko_name_path, ko_name_file = os.path.split(ko_dir_name_file_path_and_name)
        # if the paths don't exist then create them
        if os.path.isdir(ko_code_path) == False:
            os.makedirs(ko_code_path)

        if os.path.isdir(ko_name_path) == False:
            os.makedirs(ko_name_path)

        # save codes to the file
        ko_code_file = open(ko_code_file_path_and_name, 'wt', encoding='utf-8')
        ko_name_file = open(ko_dir_name_file_path_and_name, 'wt', encoding='utf-8')
        # currently the order of dictionaries in python is only preserved for version 3.6 and does not plan to make that a standard in the future and so for robustness I record the order that the codes and dirs are written to file
        order_of_keys = tuple(ko_code_dict.keys())
        for key in order_of_keys:
                ko_name_file.write(key + "\n")
                ko_code_file.write("'" + '\', \''.join(ko_code_dict[key]) + "'\n")

        ko_code_file.close()
        ko_name_file.close()

        return order_of_keys

	def convertGeneCodeToId(self, tuple_of_gene_codes, path_to_staticDb_stuff='/projects/flex1/database/staticDB'):
		"""Takes a tuple of genes code and returns a tuple of corresponding gene IDs."""
		if type(tuple_of_gene_codes) is not tuple:
			raise TypeException('Gene codes must be a tuple (even if only 1! i.e. single_tuple = (\'MG_001\',)) here type(tuple_of_gene_codes)=', type(tuple_of_gene_codes))
		add_anoconda_module = 'module add apps/anaconda3-2.3.0'
		activate_virtual_environment = 'source activate whole_cell_modelling_suite'
		change_to_lib_dir = 'cd ' + path_to_staticDb_stuff
		get_gene_id = 'python -c "from staticDB import io as sio;static_db_conn = sio();print(static_db_conn.CodeToId(' + str(tuple_of_gene_codes) + '))"'
		cmd = "ssh " + self.ssh_config_alias + ";" + add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_gene_id
		cmd_list = ["ssh", self.ssh_config_alias, add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_gene_id]
		raw_out = Connection.getOutput(cmd_list)

		# send command and get output
		output = raw_out
		output[1] = eval(str(output[1], "utf-8").rstrip())
		# it doesn't output the answer in the order you input it so we need to make a dictionary
		codeToId_dict = {}
		for out in output[1]:
			codeToId_dict[out[1]] = out[0]

		return codeToId_dict

	def checkQueue(self, job_number):
		"""This function takes a job number and returns a list of all the array numbers of that job still running."""
		grep_part_of_cmd = "squeue -ru " + self.user_name + " | grep \'" + str(job_number) + "\' | awk \'{print $1}\' | awk -F \"_\" \'{print $2}\'"

#		cmd = ["ssh", self.ssh_config_alias, grep_part_of_cmd]
		output_dict = self.checkSuccess(self.sendCommand, [grep_part_of_cmd])

		return output_dict

	def checkDiskUsage(self):
		"""This function returns disk usage details."""
		# create all the post connection commands needed
		get_disk_usage_units_command = "pan_quota | awk \'{print $1}\' | tail -n 2 | head -n 1 | sed \'s/[<>]//g\'"
		get_disk_usage_command = "pan_quota | awk \'{print $1}\' | tail -n 1"
		get_disk_usage_soft_limit_command = "pan_quota | awk \'{print $2}\' | tail -n 1"
		get_disk_usage_hard_limit_command = "pan_quota | awk \'{print $3}\' | tail -n 1"
		# combine the connection command with the post connection commands in a list (as is recomended).
		units_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_units_command]
		usage_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_command]
		soft_limit_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_soft_limit_command]
		hard_limit_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_hard_limit_command]
		# send the commands and save the exit codes and outputs
		units = Connection.getOutput(units_cmd)
		usage = Connection.getOutput(usage_cmd)
		soft_limit = Connection.getOutput(soft_limit_cmd)
		hard_limit = Connection.getOutput(hard_limit_cmd)
		# convert string outputs to floats where neccessary
		units[1] = str(units[1], "utf-8").rstrip()
		usage[1] = float(usage[1])
		soft_limit[1] = float(soft_limit[1])
		hard_limit[1] = float(hard_limit[1])
		# print some stats
		print(100 * (usage[1] / (1.0 * hard_limit[1]) ),"% of total disk space used.\n\n",hard_limit[1] - usage[1]," ",units[1]," left until hard limit.\n\n",soft_limit[1] - usage[1]," ",units[1]," left unit soft limit.", sep='')
		
		return usage, soft_limit, hard_limit, units

	def createStandardKoSubmissionScript(self, output_filename, slurm_job_name, no_of_unique_kos, path_and_name_of_unique_ko_dir_names, no_of_repetitions_of_each_ko, wholecell_model_master_dir, output_dir, path_and_name_of_ko_codes, outfile_name_and_path, errorfile_name_and_path):
		# this shouldn't change but gonna leave it there just in case
		queue_name = 'cpu'
		# set job array numbers to None so that we can check stuff has wprked later
		job_array_numbers = None
		# The maximum job array size on BC3
		max_job_array_size = 200
		# initialise output dict
		output_dict = {}
		# test that a reasonable amount of jobs has been submitted (This is not a hard and fast rule but there has to be a max and my intuition suggestss that it will start to get complicated around this level i.e. queueing and harddisk space etc)
		total_sims = no_of_unique_kos * no_of_repetitions_of_each_ko
		if total_sims > 20000:
			raise ValueError('Total amount of simulations for one batch submission must be less than 20,000, here total_sims=',total_sims)

		output_dict['total_sims'] = total_sims
		# spread simulations across array jobs
		if no_of_unique_kos <= max_job_array_size:
			no_of_unique_kos_per_array_job = 1
			no_of_arrays = no_of_unique_kos
			job_array_numbers = '1-' + str(no_of_unique_kos)
			walltime = '0-30:00:00'
		else:
			# job_array_size * no_of_unique_kos_per_array_job = no_of_unique_kos so all the factors of no_of_unique_kos is
			common_factors = [x for x in range(1, no_of_unique_kos+1) if no_of_unique_kos % x == 0]
			# make the job_array_size as large as possible such that it is less than max_job_array_size
			factor_idx = len(common_factors) - 1
			while factor_idx >= 0:
				if common_factors[factor_idx] < max_job_array_size:
					job_array_numbers = '1-' + str(common_factors[factor_idx])
					no_of_arrays = common_factors[factor_idx]
					no_of_unique_kos_per_array_job = common_factors[(len(common_factors)-1) - factor_idx]
					factor_idx = -1
				else:
					factor_idx -= 1

			# raise error if no suitable factors found!
			if job_array_numbers is None:
				raise ValueError('job_array_numbers should have been assigned by now! This suggests that it wasn\'t possible for my algorithm to split the KOs across the job array properly. Here no_of_unique_kos=', no_of_unique_kos, ' and the common factors of this number are:', common_factors)

			# add some time to the walltime because I don't think the jobs have to startat the same time
			walltime = '0-35:00:00'

		output_dict['no_of_arrays'] = no_of_arrays
		output_dict['no_of_unique_kos_per_array_job'] = no_of_unique_kos_per_array_job
		output_dict['no_of_repetitions_of_each_ko'] = no_of_repetitions_of_each_ko
		# calculate the amount of cores per array job - NOTE: for simplification we only use cores and not nodes (this is generally the fastest way to get through the queue anyway)
		no_of_cores = no_of_repetitions_of_each_ko * no_of_unique_kos_per_array_job
		output_dict['no_of_sims_per_array_job'] = no_of_cores
		output_dict['list_of_rep_dir_names'] = list(range(1, no_of_repetitions_of_each_ko + 1))
		no_of_nodes = 1
		# write the script to file
		with open(output_filename, mode='wt', encoding='utf-8') as myfile:
			myfile.write("#!/bin/bash -login" + "\n")
			myfile.write("\n")
			myfile.write("# This script was automatically created by Oliver Chalkley's whole-cell modelling suite and is based on scripts that he created." + "\n")
			myfile.write("\n")
			myfile.write("## Job name" + "\n")
			myfile.write("#SBATCH --job-name=" + slurm_job_name + "\n")
			myfile.write("\n")
			myfile.write("## What account the simulations are registered to" + "\n")
			myfile.write("#SBATCH -A Flex1" + "\n")
			myfile.write("\n")
			myfile.write("## Resource request" + "\n")
#			myfile.write("#SBATCH -n " + str(no_of_nodes) + "\n")
			myfile.write("#SBATCH --ntasks=" + str(no_of_cores) + " # No. of cores\n")
			myfile.write("#SBATCH --time=" + walltime + "\n")
			myfile.write("#SBATCH -p " + queue_name + "\n")
			myfile.write("\n")
			myfile.write("## Job array request" + "\n")
			myfile.write("#SBATCH --array=" + job_array_numbers + "\n")
			myfile.write("\n")
			myfile.write("## designate output and error files" + "\n")
			myfile.write("#SBATCH --output=" + outfile_name_and_path + "_%A_%a.out" + "\n")
			myfile.write("#SBATCH --error=" + errorfile_name_and_path + "_%A_%a.err" + "\n")
			myfile.write("\n")
			myfile.write("# print some details about the job" + "\n")
			myfile.write('echo "The Array TASK ID is: ${SLURM_ARRAY_TASK_ID}"' + "\n")
			myfile.write('echo "The Array JOB ID is: ${SLURM_ARRAY_JOB_ID}"' + "\n")
			myfile.write('echo Running on host `hostname`' + "\n")
			myfile.write('echo Time is `date`' + "\n")
			myfile.write('echo Directory is `pwd`' + "\n")
			myfile.write("\n")
			myfile.write("# load required modules" + "\n")
			myfile.write("module load apps/matlab-r2013a" + "\n")
			myfile.write('echo "Modules loaded:"' + "\n")
			myfile.write("module list" + "\n")
			myfile.write("\n")
			myfile.write("# create the master directory variable" + "\n")
			myfile.write("master=" + wholecell_model_master_dir + "\n")
			myfile.write("\n")
			myfile.write("# create output directory" + "\n")
			myfile.write("base_outDir=" + output_dir + "\n")
			myfile.write("\n")
			myfile.write("# collect the KO combos" + "\n")
			myfile.write("ko_list=" + path_and_name_of_ko_codes + "\n")
			myfile.write("ko_dir_names=" + path_and_name_of_unique_ko_dir_names + "\n")
			myfile.write("\n")
			myfile.write("# Get all the gene KOs and output folder names" + "\n")
			myfile.write('for i in `seq 1 ' + str(no_of_unique_kos_per_array_job) + '`' + "\n")
			myfile.write('do' + "\n")
			myfile.write('    Gene[${i}]=$(awk NR==$((' + str(no_of_unique_kos_per_array_job) + '*(${SLURM_ARRAY_TASK_ID}-1)+${i})) ${ko_list})' + "\n")
			myfile.write('    unique_ko_dir_name[${i}]=$(awk NR==$((' + str(no_of_unique_kos_per_array_job) + '*(${SLURM_ARRAY_TASK_ID}-1)+${i})) ${ko_dir_names})' + "\n")
			myfile.write("done" + "\n")
			myfile.write("\n")
			myfile.write("# go to master directory" + "\n")
			myfile.write("cd ${master}" + "\n")
			myfile.write("\n")
			myfile.write("# NB have limited MATLAB to a single thread" + "\n")
			myfile.write('options="-nodesktop -noFigureWindows -nosplash -singleCompThread"' + "\n")
			myfile.write("\n")
			myfile.write("# run " + str(no_of_unique_kos_per_array_job * no_of_repetitions_of_each_ko) + " simulations in parallel")
			myfile.write('echo "Running simulations (single threaded) in parallel - let\'s start the timer!"' + "\n")
			myfile.write('start=`date +%s`' + "\n")
			myfile.write("\n")
			myfile.write("# create all the directories for the diarys (the normal output will be all mixed up cause it's in parrallel!)" + "\n")
			myfile.write('for i in `seq 1 ' + str(no_of_unique_kos_per_array_job) + '`' + "\n")
			myfile.write("do" + "\n")
			myfile.write('    for j in `seq 1 ' + str(no_of_repetitions_of_each_ko) + '`' + "\n")
			myfile.write("    do" + "\n")
			myfile.write('        specific_ko="$(echo ${Gene[${i}]} | sed \'s/{//g\' | sed \'s/}//g\' | sed \"s/\'//g\" | sed \'s/\"//g\' | sed \'s/,/-/g\')/${j}"' + "\n")
			myfile.write('        mkdir -p ${base_outDir}/${unique_ko_dir_name[${i}]}/diary${j}' + "\n")
			myfile.write('        matlab ${options} -r "diary(\'${base_outDir}/${unique_ko_dir_name[${i}]}/diary${j}/diary.out\');addpath(\'${master}\');setWarnings();setPath();runSimulation(\'runner\',\'koRunner\',\'logToDisk\',true,\'outDir\',\'${base_outDir}/${unique_ko_dir_name[${i}]}/${j}\',\'jobNumber\',$((no_of_repetitions_of_each_ko*no_of_unique_kos_per_array_job*(${SLURM_ARRAY_TASK_ID}-1)+no_of_unique_kos_per_array_job*(${i}-1)+${j})),\'koList\',{{${Gene[${i}]}}});diary off;exit;" &' + "\n")
			myfile.write("    done" + "\n")
			myfile.write("done" + "\n")
			myfile.write("wait" + "\n")
			myfile.write("\n")
			myfile.write("end=`date +%s`" + "\n")
			myfile.write("runtime=$((end-start))" + "\n")
			myfile.write('echo "$((${no_of_unique_kos_per_array_job}*${no_of_repetitions_of_each_ko})) simulations took: ${runtime} seconds."')

		# give the file execute permissions
		subprocess.check_call(["chmod", "700", str(output_filename)])

		return output_dict

	def getJobIdFromSubStdOut(self, stdout):
		return int(re.search(r'\d+', stdout).group())

class C3ddb(Connection):
	def __init__(self, cluster_user_name, ssh_config_alias, path_to_key, forename_of_user, surname_of_user, user_email, base_output_path = '/scratch/users/ochalkley/wc/mg/output', base_runfiles_path = '/home/ochalkley/WholeCell/github/wc/mg/mit/runFiles', wholecell_model_master_dir = '/home/ochalkley/WholeCell/github/wc/mg/WholeCell-master'):
		Connection.__init__(self, cluster_user_name, ssh_config_alias, path_to_key, forename_of_user, surname_of_user, user_email)
		self.submit_command = 'sbatch'
		self.information_about_cluster = 'Commonwealth Computational Cloud for Data Driven Biology, Massachusetts Green High Performance Computer Center'
		self.base_output_path = base_output_path
		self.base_runfiles_path = base_runfiles_path
		self.wholecell_model_master_dir = wholecell_model_master_dir
		self.activate_venv_list = ['source activate wholecell_modelling_suite_py36']
		# create Bc3 connection to read/write with databases on flex1
		from connections import Bc3
		bc3_conn = Bc3('oc13378', 'bc3', '/users/oc13378/.ssh/uob/uob-rsa', 'Oliver', 'Chalkley', 'o.chalkley@bristol.ac.uk')
		self.db_connection = bc3_conn
		self.path_to_database_dir = '/home/ochalkley/WholeCell/github/wholecell_modelling_suite'

	#instance methhods
#	def transferFile(self, source, destination, rsync_flags = "-aP"):
#		super(bc3, self).transferFile(source, destination, rsync_flags)
#
#		return

	def convertGeneCodeToId(self, tuple_of_gene_codes, path_to_staticDb_stuff='/panfs/panasas01/bluegem-flex1/database/staticDB'):
		"""Takes a tuple of genes code and returns a tuple of corresponding gene IDs."""
		if type(tuple_of_gene_codes) is not tuple:
			raise TypeException('Gene codes must be a tuple (even if only 1! i.e. single_tuple = (\'MG_001\',)) here type(tuple_of_gene_codes)=', type(tuple_of_gene_codes))
		add_anoconda_module = 'module add languages/python-anaconda-4.2-3.5'
		activate_virtual_environment = 'source activate wholecell_modelling_suite'
		change_to_lib_dir = 'cd ' + path_to_staticDb_stuff
		get_gene_id = 'python -c "from staticDB import io as sio;static_db_conn = sio();print(static_db_conn.CodeToId(' + str(tuple_of_gene_codes) + '))"'
		cmd = "ssh " + self.db_connection.ssh_config_alias + ";" + add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_gene_id
		cmd_list = ["ssh", self.db_connection.ssh_config_alias, add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_gene_id]
		raw_out = self.db_connection.getOutput(cmd_list)

		# send command and get output
		output = raw_out
		output[1] = eval(str(output[1], "utf-8").rstrip())
		# it doesn't output the answer in the order you input it so we need to make a dictionary
		codeToId_dict = {}
		for out in output[1]:
			codeToId_dict[out[1]] = out[0]

		return codeToId_dict

	def checkQueue(self, job_number):
		"""This function takes a job number and returns a list of all the array numbers of that job still running."""
		grep_part_of_cmd = "squeue -ru " + self.user_name + " | grep \'" + str(job_number) + "\' | awk \'{print $1}\' | awk -F \"_\" \'{print $2}\'"

#		cmd = ["ssh", self.ssh_config_alias, grep_part_of_cmd]
		output_dict = self.checkSuccess(self.sendCommand, [grep_part_of_cmd])

		return output_dict

	def checkDiskUsage(self):
		"""This function returns disk usage details."""
		# create all the post connection commands needed
		get_disk_usage_units_command = "pan_quota | awk \'{print $1}\' | tail -n 2 | head -n 1 | sed \'s/[<>]//g\'"
		get_disk_usage_command = "pan_quota | awk \'{print $1}\' | tail -n 1"
		get_disk_usage_soft_limit_command = "pan_quota | awk \'{print $2}\' | tail -n 1"
		get_disk_usage_hard_limit_command = "pan_quota | awk \'{print $3}\' | tail -n 1"
		# combine the connection command with the post connection commands in a list (as is recomended).
		units_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_units_command]
		usage_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_command]
		soft_limit_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_soft_limit_command]
		hard_limit_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_hard_limit_command]
		# send the commands and save the exit codes and outputs
		units = Connection.getOutput(units_cmd)
		usage = Connection.getOutput(usage_cmd)
		soft_limit = Connection.getOutput(soft_limit_cmd)
		hard_limit = Connection.getOutput(hard_limit_cmd)
		# convert string outputs to floats where neccessary
		units[1] = str(units[1], "utf-8").rstrip()
		usage[1] = float(usage[1])
		soft_limit[1] = float(soft_limit[1])
		hard_limit[1] = float(hard_limit[1])
		# print some stats
		print(100 * (usage[1] / (1.0 * hard_limit[1]) ),"% of total disk space used.\n\n",hard_limit[1] - usage[1]," ",units[1]," left until hard limit.\n\n",soft_limit[1] - usage[1]," ",units[1]," left unit soft limit.", sep='')
		
		return usage, soft_limit, hard_limit, units

	def createStandardKoSubmissionScript(self, output_filename, slurm_job_name, no_of_unique_kos, path_and_name_of_unique_ko_dir_names, no_of_repetitions_of_each_ko, wholecell_model_master_dir, output_dir, path_and_name_of_ko_codes, outfile_name_and_path, errorfile_name_and_path):
		# this shouldn't change but gonna leave it there just in case
		queue_name = 'defq'
		# set job array numbers to None so that we can check stuff has wprked later
		job_array_numbers = None
		# The maximum job array size on BC3
		max_job_array_size = 200
		# initialise output dict
		output_dict = {}
		# test that a reasonable amount of jobs has been submitted (This is not a hard and fast rule but there has to be a max and my intuition suggestss that it will start to get complicated around this level i.e. queueing and harddisk space etc)
		total_sims = no_of_unique_kos * no_of_repetitions_of_each_ko
		if total_sims > 20000:
			raise ValueError('Total amount of simulations for one batch submission must be less than 20,000, here total_sims=',total_sims)

		output_dict['total_sims'] = total_sims
		# spread simulations across array jobs
		if no_of_unique_kos <= max_job_array_size:
			no_of_unique_kos_per_array_job = 1
			no_of_arrays = no_of_unique_kos
			job_array_numbers = '1-' + str(no_of_unique_kos)
			walltime = '0-30:00:00'
		else:
			# job_array_size * no_of_unique_kos_per_array_job = no_of_unique_kos so all the factors of no_of_unique_kos is
			common_factors = [x for x in range(1, no_of_unique_kos+1) if no_of_unique_kos % x == 0]
			# make the job_array_size as large as possible such that it is less than max_job_array_size
			factor_idx = len(common_factors) - 1
			while factor_idx >= 0:
				if common_factors[factor_idx] < max_job_array_size:
					job_array_numbers = '1-' + str(common_factors[factor_idx])
					no_of_arrays = common_factors[factor_idx]
					no_of_unique_kos_per_array_job = common_factors[(len(common_factors)-1) - factor_idx]
					factor_idx = -1
				else:
					factor_idx -= 1

			# raise error if no suitable factors found!
			if job_array_numbers is None:
				raise ValueError('job_array_numbers should have been assigned by now! This suggests that it wasn\'t possible for my algorithm to split the KOs across the job array properly. Here no_of_unique_kos=', no_of_unique_kos, ' and the common factors of this number are:', common_factors)

			# add some time to the walltime because I don't think the jobs have to startat the same time
			walltime = '0-35:00:00'

		output_dict['no_of_arrays'] = no_of_arrays
		output_dict['no_of_unique_kos_per_array_job'] = no_of_unique_kos_per_array_job
		output_dict['no_of_repetitions_of_each_ko'] = no_of_repetitions_of_each_ko
		# calculate the amount of cores per array job - NOTE: for simplification we only use cores and not nodes (this is generally the fastest way to get through the queue anyway)
		no_of_cores = no_of_repetitions_of_each_ko * no_of_unique_kos_per_array_job
		output_dict['no_of_sims_per_array_job'] = no_of_cores
		output_dict['list_of_rep_dir_names'] = list(range(1, no_of_repetitions_of_each_ko + 1))
		no_of_nodes = 1
		# write the script to file
		with open(output_filename, mode='wt', encoding='utf-8') as myfile:
			myfile.write("#!/bin/bash" + "\n")
			myfile.write("\n")
			myfile.write("# This script was automatically created by Oliver Chalkley's whole-cell modelling suite and is based on scripts that he created." + "\n")
			myfile.write("\n")
			myfile.write("## Job name" + "\n")
			myfile.write("#SBATCH --job-name=" + slurm_job_name + "\n")
			myfile.write("\n")
			myfile.write("## Resource request" + "\n")
#			myfile.write("#SBATCH -n " + str(no_of_nodes) + "\n")
			myfile.write("#SBATCH --ntasks=" + str(no_of_cores) + " # No. of cores\n")
			myfile.write("#SBATCH --time=" + walltime + "\n")
			myfile.write("#SBATCH -p " + queue_name + "\n")
			myfile.write("#SBATCH --mem-per-cpu=10000" + "\n")
			myfile.write("\n")
			myfile.write("## Job array request" + "\n")
			myfile.write("#SBATCH --array=" + job_array_numbers + "\n")
			myfile.write("\n")
			myfile.write("## designate output and error files" + "\n")
			myfile.write("#SBATCH --output=" + outfile_name_and_path + "_%A_%a.out" + "\n")
			myfile.write("#SBATCH --error=" + errorfile_name_and_path + "_%A_%a.err" + "\n")
			myfile.write("\n")
			myfile.write("# print some details about the job" + "\n")
			myfile.write('echo "The Array TASK ID is: ${SLURM_ARRAY_TASK_ID}"' + "\n")
			myfile.write('echo "The Array JOB ID is: ${SLURM_ARRAY_JOB_ID}"' + "\n")
			myfile.write('echo Running on host `hostname`' + "\n")
			myfile.write('echo Time is `date`' + "\n")
			myfile.write('echo Directory is `pwd`' + "\n")
			myfile.write("\n")
			myfile.write("# load required modules" + "\n")
			myfile.write("module load mit/matlab/2013a" + "\n")
			myfile.write('echo "Modules loaded:"' + "\n")
			myfile.write("module list" + "\n")
			myfile.write("\n")
			myfile.write("# create the master directory variable" + "\n")
			myfile.write("master=" + wholecell_model_master_dir + "\n")
			myfile.write("\n")
			myfile.write("# create output directory" + "\n")
			myfile.write("base_outDir=" + output_dir + "\n")
			myfile.write("\n")
			myfile.write("# collect the KO combos" + "\n")
			myfile.write("ko_list=" + path_and_name_of_ko_codes + "\n")
			myfile.write("ko_dir_names=" + path_and_name_of_unique_ko_dir_names + "\n")
			myfile.write("\n")
			myfile.write("# Get all the gene KOs and output folder names" + "\n")
			myfile.write('for i in `seq 1 ' + str(no_of_unique_kos_per_array_job) + '`' + "\n")
			myfile.write('do' + "\n")
			myfile.write('    Gene[${i}]=$(awk NR==$((' + str(no_of_unique_kos_per_array_job) + '*(${SLURM_ARRAY_TASK_ID}-1)+${i})) ${ko_list})' + "\n")
			myfile.write('    unique_ko_dir_name[${i}]=$(awk NR==$((' + str(no_of_unique_kos_per_array_job) + '*(${SLURM_ARRAY_TASK_ID}-1)+${i})) ${ko_dir_names})' + "\n")
			myfile.write("done" + "\n")
			myfile.write("\n")
			myfile.write("# go to master directory" + "\n")
			myfile.write("cd ${master}" + "\n")
			myfile.write("\n")
			myfile.write("# NB have limited MATLAB to a single thread" + "\n")
			myfile.write('options="-nodesktop -noFigureWindows -nosplash -singleCompThread"' + "\n")
			myfile.write("\n")
			myfile.write("# run " + str(no_of_unique_kos_per_array_job * no_of_repetitions_of_each_ko) + " simulations in parallel")
			myfile.write('echo "Running simulations (single threaded) in parallel - let\'s start the timer!"' + "\n")
			myfile.write('start=`date +%s`' + "\n")
			myfile.write("\n")
			myfile.write("# create all the directories for the diarys (the normal output will be all mixed up cause it's in parrallel!)" + "\n")
			myfile.write('for i in `seq 1 ' + str(no_of_unique_kos_per_array_job) + '`' + "\n")
			myfile.write("do" + "\n")
			myfile.write('    for j in `seq 1 ' + str(no_of_repetitions_of_each_ko) + '`' + "\n")
			myfile.write("    do" + "\n")
			myfile.write('        specific_ko="$(echo ${Gene[${i}]} | sed \'s/{//g\' | sed \'s/}//g\' | sed \"s/\'//g\" | sed \'s/\"//g\' | sed \'s/,/-/g\')/${j}"' + "\n")
			myfile.write('        mkdir -p ${base_outDir}/${unique_ko_dir_name[${i}]}/diary${j}' + "\n")
			myfile.write('        matlab ${options} -r "diary(\'${base_outDir}/${unique_ko_dir_name[${i}]}/diary${j}/diary.out\');addpath(\'${master}\');setWarnings();setPath();runSimulation(\'runner\',\'koRunner\',\'logToDisk\',true,\'outDir\',\'${base_outDir}/${unique_ko_dir_name[${i}]}/${j}\',\'jobNumber\',$((no_of_repetitions_of_each_ko*no_of_unique_kos_per_array_job*(${SLURM_ARRAY_TASK_ID}-1)+no_of_unique_kos_per_array_job*(${i}-1)+${j})),\'koList\',{{${Gene[${i}]}}});diary off;exit;" &' + "\n")
			myfile.write("    done" + "\n")
			myfile.write("done" + "\n")
			myfile.write("wait" + "\n")
			myfile.write("\n")
			myfile.write("end=`date +%s`" + "\n")
			myfile.write("runtime=$((end-start))" + "\n")
			myfile.write('echo "$((${no_of_unique_kos_per_array_job}*${no_of_repetitions_of_each_ko})) simulations took: ${runtime} seconds."')

		# give the file execute permissions
		subprocess.check_call(["chmod", "700", str(output_filename)])

		return output_dict

	def getJobIdFromSubStdOut(self, stdout):
		return int(re.search(r'\d+', stdout).group())

class C3ddbWithOutScratch(Connection):
	def __init__(self, cluster_user_name, ssh_config_alias, path_to_key, forename_of_user, surname_of_user, user_email, base_output_path = '/home/ochalkley/wc/mg/output', base_runfiles_path = '/home/ochalkley/WholeCell/github/wc/mg/mit/runFiles', wholecell_model_master_dir = '/home/ochalkley/WholeCell/github/wc/mg/WholeCell-master'):
		Connection.__init__(self, cluster_user_name, ssh_config_alias, path_to_key, forename_of_user, surname_of_user, user_email)
		self.submit_command = 'sbatch'
		self.information_about_cluster = 'Commonwealth Computational Cloud for Data Driven Biology, Massachusetts Green High Performance Computer Center'
		self.base_output_path = base_output_path
		self.base_runfiles_path = base_runfiles_path
		self.wholecell_model_master_dir = wholecell_model_master_dir
		self.activate_venv_list = ['source activate wholecell_modelling_suite_py36']
		# create Bc3 connection to read/write with databases on flex1
		from connections import Bc3
		bc3_conn = Bc3('oc13378', 'bc3', '/users/oc13378/.ssh/uob/uob-rsa', 'Oliver', 'Chalkley', 'o.chalkley@bristol.ac.uk')
		self.db_connection = bc3_conn
		self.path_to_database_dir = '/home/ochalkley/WholeCell/github/wholecell_modelling_suite'

	#instance methhods
#	def transferFile(self, source, destination, rsync_flags = "-aP"):
#		super(bc3, self).transferFile(source, destination, rsync_flags)
#
#		return

	def convertGeneCodeToId(self, tuple_of_gene_codes, path_to_staticDb_stuff='/panfs/panasas01/bluegem-flex1/database/staticDB'):
		"""Takes a tuple of genes code and returns a tuple of corresponding gene IDs."""
		if type(tuple_of_gene_codes) is not tuple:
			raise TypeException('Gene codes must be a tuple (even if only 1! i.e. single_tuple = (\'MG_001\',)) here type(tuple_of_gene_codes)=', type(tuple_of_gene_codes))
		add_anoconda_module = 'module add languages/python-anaconda-4.2-3.5'
		activate_virtual_environment = 'source activate wholecell_modelling_suite'
		change_to_lib_dir = 'cd ' + path_to_staticDb_stuff
		get_gene_id = 'python -c "from staticDB import io as sio;static_db_conn = sio();print(static_db_conn.CodeToId(' + str(tuple_of_gene_codes) + '))"'
		cmd = "ssh " + self.db_connection.ssh_config_alias + ";" + add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_gene_id
		cmd_list = ["ssh", self.db_connection.ssh_config_alias, add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_gene_id]
		raw_out = self.db_connection.getOutput(cmd_list)

		# send command and get output
		output = raw_out
		output[1] = eval(str(output[1], "utf-8").rstrip())
		# it doesn't output the answer in the order you input it so we need to make a dictionary
		codeToId_dict = {}
		for out in output[1]:
			codeToId_dict[out[1]] = out[0]

		return codeToId_dict

	def checkQueue(self, job_number):
		"""This function takes a job number and returns a list of all the array numbers of that job still running."""
		grep_part_of_cmd = "squeue -ru " + self.user_name + " | grep \'" + str(job_number) + "\' | awk \'{print $1}\' | awk -F \"_\" \'{print $2}\'"

#		cmd = ["ssh", self.ssh_config_alias, grep_part_of_cmd]
		output_dict = self.checkSuccess(self.sendCommand, [grep_part_of_cmd])

		return output_dict

	def checkDiskUsage(self):
		"""This function returns disk usage details."""
		# create all the post connection commands needed
		get_disk_usage_units_command = "pan_quota | awk \'{print $1}\' | tail -n 2 | head -n 1 | sed \'s/[<>]//g\'"
		get_disk_usage_command = "pan_quota | awk \'{print $1}\' | tail -n 1"
		get_disk_usage_soft_limit_command = "pan_quota | awk \'{print $2}\' | tail -n 1"
		get_disk_usage_hard_limit_command = "pan_quota | awk \'{print $3}\' | tail -n 1"
		# combine the connection command with the post connection commands in a list (as is recomended).
		units_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_units_command]
		usage_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_command]
		soft_limit_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_soft_limit_command]
		hard_limit_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_hard_limit_command]
		# send the commands and save the exit codes and outputs
		units = Connection.getOutput(units_cmd)
		usage = Connection.getOutput(usage_cmd)
		soft_limit = Connection.getOutput(soft_limit_cmd)
		hard_limit = Connection.getOutput(hard_limit_cmd)
		# convert string outputs to floats where neccessary
		units[1] = str(units[1], "utf-8").rstrip()
		usage[1] = float(usage[1])
		soft_limit[1] = float(soft_limit[1])
		hard_limit[1] = float(hard_limit[1])
		# print some stats
		print(100 * (usage[1] / (1.0 * hard_limit[1]) ),"% of total disk space used.\n\n",hard_limit[1] - usage[1]," ",units[1]," left until hard limit.\n\n",soft_limit[1] - usage[1]," ",units[1]," left unit soft limit.", sep='')
		
		return usage, soft_limit, hard_limit, units

	def createStandardKoSubmissionScript(self, output_filename, slurm_job_name, no_of_unique_kos, path_and_name_of_unique_ko_dir_names, no_of_repetitions_of_each_ko, wholecell_model_master_dir, output_dir, path_and_name_of_ko_codes, outfile_name_and_path, errorfile_name_and_path):
		# this shouldn't change but gonna leave it there just in case
		queue_name = 'defq'
		# set job array numbers to None so that we can check stuff has wprked later
		job_array_numbers = None
		# The maximum job array size on BC3
		max_job_array_size = 200
		# initialise output dict
		output_dict = {}
		# test that a reasonable amount of jobs has been submitted (This is not a hard and fast rule but there has to be a max and my intuition suggestss that it will start to get complicated around this level i.e. queueing and harddisk space etc)
		total_sims = no_of_unique_kos * no_of_repetitions_of_each_ko
		if total_sims > 20000:
			raise ValueError('Total amount of simulations for one batch submission must be less than 20,000, here total_sims=',total_sims)

		output_dict['total_sims'] = total_sims
		# spread simulations across array jobs
		if no_of_unique_kos <= max_job_array_size:
			no_of_unique_kos_per_array_job = 1
			no_of_arrays = no_of_unique_kos
			job_array_numbers = '1-' + str(no_of_unique_kos)
			walltime = '0-30:00:00'
		else:
			# job_array_size * no_of_unique_kos_per_array_job = no_of_unique_kos so all the factors of no_of_unique_kos is
			common_factors = [x for x in range(1, no_of_unique_kos+1) if no_of_unique_kos % x == 0]
			# make the job_array_size as large as possible such that it is less than max_job_array_size
			factor_idx = len(common_factors) - 1
			while factor_idx >= 0:
				if common_factors[factor_idx] < max_job_array_size:
					job_array_numbers = '1-' + str(common_factors[factor_idx])
					no_of_arrays = common_factors[factor_idx]
					no_of_unique_kos_per_array_job = common_factors[(len(common_factors)-1) - factor_idx]
					factor_idx = -1
				else:
					factor_idx -= 1

			# raise error if no suitable factors found!
			if job_array_numbers is None:
				raise ValueError('job_array_numbers should have been assigned by now! This suggests that it wasn\'t possible for my algorithm to split the KOs across the job array properly. Here no_of_unique_kos=', no_of_unique_kos, ' and the common factors of this number are:', common_factors)

			# add some time to the walltime because I don't think the jobs have to startat the same time
			walltime = '0-35:00:00'

		output_dict['no_of_arrays'] = no_of_arrays
		output_dict['no_of_unique_kos_per_array_job'] = no_of_unique_kos_per_array_job
		output_dict['no_of_repetitions_of_each_ko'] = no_of_repetitions_of_each_ko
		# calculate the amount of cores per array job - NOTE: for simplification we only use cores and not nodes (this is generally the fastest way to get through the queue anyway)
		no_of_cores = no_of_repetitions_of_each_ko * no_of_unique_kos_per_array_job
		output_dict['no_of_sims_per_array_job'] = no_of_cores
		output_dict['list_of_rep_dir_names'] = list(range(1, no_of_repetitions_of_each_ko + 1))
		no_of_nodes = 1
		# write the script to file
		with open(output_filename, mode='wt', encoding='utf-8') as myfile:
			myfile.write("#!/bin/bash" + "\n")
			myfile.write("\n")
			myfile.write("# This script was automatically created by Oliver Chalkley's whole-cell modelling suite and is based on scripts that he created." + "\n")
			myfile.write("\n")
			myfile.write("## Job name" + "\n")
			myfile.write("#SBATCH --job-name=" + slurm_job_name + "\n")
			myfile.write("\n")
			myfile.write("## Resource request" + "\n")
#			myfile.write("#SBATCH -n " + str(no_of_nodes) + "\n")
			myfile.write("#SBATCH --ntasks=" + str(no_of_cores) + " # No. of cores\n")
			myfile.write("#SBATCH --time=" + walltime + "\n")
			myfile.write("#SBATCH -p " + queue_name + "\n")
			myfile.write("#SBATCH --mem-per-cpu=10000" + "\n")
			myfile.write("\n")
			myfile.write("## Job array request" + "\n")
			myfile.write("#SBATCH --array=" + job_array_numbers + "\n")
			myfile.write("\n")
			myfile.write("## designate output and error files" + "\n")
			myfile.write("#SBATCH --output=" + outfile_name_and_path + "_%A_%a.out" + "\n")
			myfile.write("#SBATCH --error=" + errorfile_name_and_path + "_%A_%a.err" + "\n")
			myfile.write("\n")
			myfile.write("# print some details about the job" + "\n")
			myfile.write('echo "The Array TASK ID is: ${SLURM_ARRAY_TASK_ID}"' + "\n")
			myfile.write('echo "The Array JOB ID is: ${SLURM_ARRAY_JOB_ID}"' + "\n")
			myfile.write('echo Running on host `hostname`' + "\n")
			myfile.write('echo Time is `date`' + "\n")
			myfile.write('echo Directory is `pwd`' + "\n")
			myfile.write("\n")
			myfile.write("# load required modules" + "\n")
			myfile.write("module load mit/matlab/2013a" + "\n")
			myfile.write('echo "Modules loaded:"' + "\n")
			myfile.write("module list" + "\n")
			myfile.write("\n")
			myfile.write("# create the master directory variable" + "\n")
			myfile.write("master=" + wholecell_model_master_dir + "\n")
			myfile.write("\n")
			myfile.write("# create output directory" + "\n")
			myfile.write("base_outDir=" + output_dir + "\n")
			myfile.write("\n")
			myfile.write("# collect the KO combos" + "\n")
			myfile.write("ko_list=" + path_and_name_of_ko_codes + "\n")
			myfile.write("ko_dir_names=" + path_and_name_of_unique_ko_dir_names + "\n")
			myfile.write("\n")
			myfile.write("# Get all the gene KOs and output folder names" + "\n")
			myfile.write('for i in `seq 1 ' + str(no_of_unique_kos_per_array_job) + '`' + "\n")
			myfile.write('do' + "\n")
			myfile.write('    Gene[${i}]=$(awk NR==$((' + str(no_of_unique_kos_per_array_job) + '*(${SLURM_ARRAY_TASK_ID}-1)+${i})) ${ko_list})' + "\n")
			myfile.write('    unique_ko_dir_name[${i}]=$(awk NR==$((' + str(no_of_unique_kos_per_array_job) + '*(${SLURM_ARRAY_TASK_ID}-1)+${i})) ${ko_dir_names})' + "\n")
			myfile.write("done" + "\n")
			myfile.write("\n")
			myfile.write("# go to master directory" + "\n")
			myfile.write("cd ${master}" + "\n")
			myfile.write("\n")
			myfile.write("# NB have limited MATLAB to a single thread" + "\n")
			myfile.write('options="-nodesktop -noFigureWindows -nosplash -singleCompThread"' + "\n")
			myfile.write("\n")
			myfile.write("# run " + str(no_of_unique_kos_per_array_job * no_of_repetitions_of_each_ko) + " simulations in parallel")
			myfile.write('echo "Running simulations (single threaded) in parallel - let\'s start the timer!"' + "\n")
			myfile.write('start=`date +%s`' + "\n")
			myfile.write("\n")
			myfile.write("# create all the directories for the diarys (the normal output will be all mixed up cause it's in parrallel!)" + "\n")
			myfile.write('for i in `seq 1 ' + str(no_of_unique_kos_per_array_job) + '`' + "\n")
			myfile.write("do" + "\n")
			myfile.write('    for j in `seq 1 ' + str(no_of_repetitions_of_each_ko) + '`' + "\n")
			myfile.write("    do" + "\n")
			myfile.write('        specific_ko="$(echo ${Gene[${i}]} | sed \'s/{//g\' | sed \'s/}//g\' | sed \"s/\'//g\" | sed \'s/\"//g\' | sed \'s/,/-/g\')/${j}"' + "\n")
			myfile.write('        mkdir -p ${base_outDir}/${unique_ko_dir_name[${i}]}/diary${j}' + "\n")
			myfile.write('        matlab ${options} -r "diary(\'${base_outDir}/${unique_ko_dir_name[${i}]}/diary${j}/diary.out\');addpath(\'${master}\');setWarnings();setPath();runSimulation(\'runner\',\'koRunner\',\'logToDisk\',true,\'outDir\',\'${base_outDir}/${unique_ko_dir_name[${i}]}/${j}\',\'jobNumber\',$((no_of_repetitions_of_each_ko*no_of_unique_kos_per_array_job*(${SLURM_ARRAY_TASK_ID}-1)+no_of_unique_kos_per_array_job*(${i}-1)+${j})),\'koList\',{{${Gene[${i}]}}});diary off;exit;" &' + "\n")
			myfile.write("    done" + "\n")
			myfile.write("done" + "\n")
			myfile.write("wait" + "\n")
			myfile.write("\n")
			myfile.write("end=`date +%s`" + "\n")
			myfile.write("runtime=$((end-start))" + "\n")
			myfile.write('echo "$((${no_of_unique_kos_per_array_job}*${no_of_repetitions_of_each_ko})) simulations took: ${runtime} seconds."')

		# give the file execute permissions
		subprocess.check_call(["chmod", "700", str(output_filename)])

		return output_dict

	def getJobIdFromSubStdOut(self, stdout):
		return int(re.search(r'\d+', stdout).group())
