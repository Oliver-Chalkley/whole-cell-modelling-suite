from abc import ABCMeta, abstractmethod
import sys
sys.path.insert(0, '/home/oli/git/published_libraries/computer_communication_framework')
from computer_communication_framework.base_connection import BasePbs, BaseSlurm
import subprocess
import re
import datetime

class Bg(BaseSlurm):
    def __init__(self):
        pass

class Bc3(BasePbs):
    """
    Because this initialises it's parents and it's grandparents class and so in addition to the following arguments you will also have to pass the arguments to satisfy the parent and grandparent classes.

    This is one of the final layers of te connection classes. The purpose of this layer is to contain all the methods and variables that relate only to the whole-cell model jobs related to BlueCrystal Phase III.

    Args:
        path_to_flex1 (str): Flex1 is a disk that the Minimal genome group uses as the main read/write disk for the Bristol supercomputers and also for the storage of communal data and databases etc. If a cluster does not have direct access to flex1 one then a class needs to be written without the path_to_flex1 variable and a cluster connection needs to be passed as the db_connection variable.
        relative_to_flex1_path_to_communual_data (str): The communual data directory can be found at path_to_flex1/relative_to_flex1_path_to_communual_data

    NOTE: The instance variable self.db_connection = self may seem confusing and so will be explained here. If one has access to an off campus cluster then that will not have access to the communual data on Flex1. In order to give off-campus access to the communual data we created a self.db_connection instance variable which needs to be a connection that has direct access to the data. Obviously connections that already have direct access don't NEED the self.db_connection variable but in order to be consistent so that higher level programs know where to access this data we also create the variable for connections with direct access and simply pass itself to that variable.
    """

    def __init__(self, cluster_user_name, ssh_config_alias, forename_of_user, surname_of_user, user_email, base_output_path, base_runfiles_path, affiliation):

        BasePbs.__init__(self, cluster_user_name, ssh_config_alias, forename_of_user, surname_of_user, user_email, base_output_path, base_runfiles_path, 'BlueCrystal Phase 3: Advanced Computing Research Centre, University of Bristol.', affiliation)

    def checkDiskUsage(self):
        """
        This function returns disk usage details. BC3 uses the command pan_quota in order to get a users disk quota, here we use sed, awk, head, and tail to extract the hard limit, soft limit, usage and the units.
                
        Returns:
            output_dict (dict): Has keys usage, soft_limit, hard_limit and units.

        """
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
        units = self.localShellCommand(units_cmd)
        usage = self.localShellCommand(usage_cmd)
        soft_limit = self.localShellCommand(soft_limit_cmd)
        hard_limit = self.localShellCommand(hard_limit_cmd)
        # convert string outputs to floats where neccessary
        units[1] = str(units[1], "utf-8").rstrip()
        usage[1] = float(usage[1])
        soft_limit[1] = float(soft_limit[1])
        hard_limit[1] = float(hard_limit[1])
        # print some stats
        print(100 * (usage[1] / (1.0 * hard_limit[1]) ),"% of total disk space used.\n\n",hard_limit[1] - usage[1]," ",units[1]," left until hard limit.\n\n",soft_limit[1] - usage[1]," ",units[1]," left unit soft limit.", sep='')
        
        output_dict = {'usage': usage, 'soft_limit': soft_limit, 'hard_limit': hard_limit, 'units': units}

        return output_dict

class Karr2012General(metaclass=ABCMeta):
    """
    Contains all the attributes neccessary for connection class that wants to interact with infra-structure created by Oliver Chalkley for the Whole-Cell model (Karr et al. 2012).
    """

    def __init__(self, wholecell_master_dir, activate_virtual_environment_list, path_to_flex1, relative_to_flex1_path_to_communual_data, db_connection):
        self.wholecell_master_dir = wholecell_master_dir
        self.activate_virtual_environment_list = activate_virtual_environment_list
        self.path_to_flex1 = path_to_flex1
        self.relative_to_flex1_path_to_communual_data = relative_to_flex1_path_to_communual_data
        self.path_to_database_dir = self.path_to_flex1 + '/'  + self.relative_to_flex1_path_to_communual_data
        self.db_connection = db_connection

    def getGeneInfo(self, tuple_of_gene_codes):
        """
        NOTE: It is advised that you use this data through the analysis part of the library as this is a bit raw.
        
        This function takes a tuple of gene codes and returns some information about their function and their single gene essentiality in a dictionary. The raw output from the database is retrieved from the 'self.useStaticDbFunction' function and processed here.

        Args:
            tuple_of_gene_codes (tuple of strings): Each string is a gene-code as dictated by Karr et al. 2012.

        Returns:
            gene_info (dict): A dictionary with keys 'code', 'type', 'name', 'symbol', 'functional_unit', 'deletion_phenotype', 'essential_in_model', 'essential_in_experiment'.
        """

        raw_out = self.useStaticDbFunction([tuple_of_gene_codes], 'CodeToInfo')
        if raw_out[0] == 0:
            as_list = eval(raw_out[1].strip().decode('ascii'))
            list_of_column_names = ['code', 'type', 'name', 'symbol', 'functional_unit', 'deletion_phenotype', 'essential_in_model', 'essential_in_experiment']
            gene_info = {list_of_column_names[name_idx]: [as_list[element_idx][name_idx] for element_idx in range(len(as_list))] for name_idx in range(len(list_of_column_names))}
        else:
            raise ValueError("Failed to retrieve sql data. Query returned: ", raw_out)

        return gene_info

    def useStaticDbFunction(self, list_of_function_inputs, function_call):
        """
        This function allows you to a call a pre-made function from the static.db io library so that you can quickly and easily retrieve data whilst keeping code to a minimum.

        Args:
            function_call (str): The name of the function in the static.db io library that you wish to use.
            list_of_function_inputs (list of unknown contents): This is a list of the arguments that need to be passed to the 'function_call' function.
            path_to_staticDb_stuff (str): path to the staticDB directory.
        """

        path_to_staticDb_stuff = self.relative_to_flex1_path_to_communual_data + '/staticDB'
        add_anoconda_module = self.activate_virtual_environment_list[0]
        activate_virtual_environment = self.activate_virtual_environment_list[1]
        change_to_lib_dir = 'cd ' + path_to_staticDb_stuff
        get_data = 'python -c "from staticDB import io as sio;static_db_conn = sio();print(static_db_conn.' + function_call + '(' + ','.join(map(str, list_of_function_inputs)) + '))"'
        cmd = "ssh " + self.ssh_config_alias + ";" + add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_data
        cmd_list = ["ssh", self.ssh_config_alias, add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_data]
        raw_out = Connection.getOutput(cmd_list)

        return raw_out


    def sendSqlToStaticDb(self, sql_command):
        """
        Takes an SQLITE3 command as a string and sends it to static.db and returns the raw output.

        Args:
            sql_command (str): SQLITE3 command that needs to be executed on the static database.
            path_to_staticDb_stuff (str): Path to the staticDB directory.

        Returns:
            raw_out (??): Raw output from the Connection.getOutput function.
        """
        path_to_staticDb_stuff = self.relative_to_flex1_path_to_communual_data + '/staticDB'
        add_anoconda_module = 'module add languages/python-anaconda-4.2-3.5'
        activate_virtual_environment = 'source activate wholecell_modelling_suite'
        change_to_lib_dir = 'cd ' + path_to_staticDb_stuff
        get_data = 'python -c "from staticDB import io as sio;static_db_conn = sio();print(static_db_conn.raw_sql_query(\'' + sql_command + '\'))"'
        cmd = "ssh " + self.ssh_config_alias + ";" + add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_data
        cmd_list = ["ssh", self.ssh_config_alias, add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_data]
        raw_out = Connection.getOutput(cmd_list)

        return raw_out

    def convertGeneCodeToId(self, tuple_of_gene_codes):
        """
        Takes a tuple of genes code and returns a dictionary of codes to corresponding gene IDs.

        Args:
            tuple_of_genes (tuple of strings): Each string is a gene code as dictated by Karr et al. 2012.
            path_to_staticDb_stuff (str): The path to the staticDB directory.

        Returns:
           code_to_id_dict (dict): Each key is a gene code and is correspponding value is the ID that represents the gene code in the static database. 
        """

        if type(tuple_of_gene_codes) is not tuple:
                raise TypeException('Gene codes must be a tuple (even if only 1! i.e. single_tuple = (\'MG_001\',)) here type(tuple_of_gene_codes)=', type(tuple_of_gene_codes))
        path_to_staticDb_stuff = self.relative_to_flex1_path_to_communual_data + '/staticDB'
        add_anoconda_module = self.activate_virtual_environment_list[0]
        activate_virtual_environment = self.activate_virtual_environment_list[1]
        change_to_lib_dir = 'cd ' + path_to_staticDb_stuff
        get_gene_id = 'python -c "from staticDB import io as sio;static_db_conn = sio();print(static_db_conn.CodeToId(' + str(tuple_of_gene_codes) + '))"'
        cmd = "ssh " + self.ssh_config_alias + ";" + add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_gene_id
        cmd_list = ["ssh", self.ssh_config_alias, add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_gene_id]
        raw_out = Connection.getOutput(cmd_list)

        # send command and get output
        output = raw_out
        output[1] = eval(str(output[1], "utf-8").rstrip())
        # it doesn't output the answer in the order you input it so we need to make a dictionary
        code_to_id_dict = {}
        for out in output[1]:
                code_to_id_dict[out[1]] = out[0]

        return code_to_id_dict

class Karr2012BgKos(Karr2012General, Bg):
    def __init__(self, cluster_user_name, ssh_config_alias, forename_of_user, surname_of_user, user_email, base_output_path, base_runfiles_path, wholecell_master_dir, affiliation = 'Minimal Genome Group, Bristol Centre for Complexity Science, BrisSynBio, University of Bristol.', activate_virtual_environment_list = ['module add languages/python-anaconda-4.2-3.5', 'source activate wholecell_modelling_suite'], path_to_flex1 = '/panfs/panasas01/bluegem-flex1', relative_to_flex1_path_to_communual_data = 'database'):
        Bg.__init__(cluster_user_name, ssh_config_alias, forename_of_user, surname_of_user, user_email, base_output_path, base_runfiles_path, affiliation)
        Karr2012General.__init__(wholecell_master_dir, activate_virtual_environment_list, path_to_flex1, relative_to_flex1_path_to_communual_data, db_connection)
        self.db_connection = self

# NEED TO ADD KO SUBMISSION SCRIPT FUNCTION !!!!!

class Karr2012Bc3Kos(Bc3, Karr2012General):
    def __init__(self, cluster_user_name, ssh_config_alias, forename_of_user, surname_of_user, user_email, base_output_path, base_runfiles_path, wholecell_master_dir, affiliation = 'Minimal Genome Group, Bristol Centre for Complexity Science, BrisSynBio, University of Bristol.', activate_virtual_environment_list = ['module add languages/python-anaconda-4.2-3.5', 'source activate wholecell_modelling_suite'], path_to_flex1 = '/panfs/panasas01/bluegem-flex1', relative_to_flex1_path_to_communual_data = 'database'):
        Bc3.__init__(self, cluster_user_name, ssh_config_alias, forename_of_user, surname_of_user, user_email, base_output_path, base_runfiles_path, affiliation)
        self.db_connection = self
        Karr2012General.__init__(self, wholecell_master_dir, activate_virtual_environment_list, path_to_flex1, relative_to_flex1_path_to_communual_data, self.db_connection)

    def createWcmKoScript(self, name_of_job, wholecell_model_master_dir, output_dir, outfiles_path, errorfiles_path, path_and_name_of_ko_codes, path_and_name_of_unique_ko_dir_names, no_of_unique_ko_sets, no_of_repetitions_of_each_ko, queue_name = 'short'):

        submission_script_filename = name_of_job + '_submission.sh'
        # assign None so that we can check things worked later
        job_array_numbers = None
        # The maximum job array size on BC3
        max_job_array_size = 500
        # initialise output dict
        output_dict = {}
        # test that a reasonable amount of jobs has been submitted (This is not a hard and fast rule but there has to be a max and my intuition suggestss that it will start to get complicated around this level i.e. queueing and harddisk space etc)
        total_sims = no_of_unique_ko_sets * no_of_repetitions_of_each_ko
        if total_sims > 20000:
                raise ValueError('Total amount of simulations for one batch submission must be less than 20,000, here total_sims=',total_sims)

        output_dict['total_sims'] = total_sims
        # spread simulations across array jobs
        if no_of_unique_ko_sets <= max_job_array_size:
                no_of_unique_ko_sets_per_array_job = 1
                no_of_arrays = no_of_unique_ko_sets
                job_array_numbers = '1-' + str(no_of_unique_ko_sets)
                walltime = '30:00:00'
        else:
                # job_array_size * no_of_unique_ko_sets_per_array_job = no_of_unique_ko_sets so all the factors of no_of_unique_ko_sets is
                common_factors = [x for x in range(1, no_of_unique_ko_sets+1) if no_of_unique_ko_sets % x == 0]
                # make the job_array_size as large as possible such that it is less than max_job_array_size
                factor_idx = len(common_factors) - 1
                while factor_idx >= 0:
                        if common_factors[factor_idx] < max_job_array_size:
                                job_array_numbers = '1-' + str(common_factors[factor_idx])
                                no_of_arrays = common_factors[factor_idx]
                                no_of_unique_ko_sets_per_array_job = common_factors[(len(common_factors)-1) - factor_idx]
                                factor_idx = -1
                        else:
                                factor_idx -= 1

                # raise error if no suitable factors found!
                if job_array_numbers is None:
                        raise ValueError('job_array_numbers should have been assigned by now! This suggests that it wasn\'t possible for my algorithm to split the KOs across the job array properly. Here no_of_unique_ko_sets=', no_of_unique_ko_sets, ' and the common factors of this number are:', common_factors)

                # add some time to the walltime because I don't think the jobs have to startat the same time
                walltime = '35:00:00'

        output_dict['no_of_arrays'] = no_of_arrays
        output_dict['no_of_unique_ko_sets_per_array_job'] = no_of_unique_ko_sets_per_array_job
        output_dict['no_of_repetitions_of_each_ko'] = no_of_repetitions_of_each_ko
        # calculate the amount of cores per array job - NOTE: for simplification we only use cores and not nodes (this is generally the fastest way to get through the queue anyway)
        no_of_cores = no_of_repetitions_of_each_ko * no_of_unique_ko_sets_per_array_job
        output_dict['no_of_sims_per_array_job'] = no_of_cores
        output_dict['list_of_rep_dir_names'] = list(range(1, no_of_repetitions_of_each_ko + 1))
        no_of_nodes = 1

        # We use the standard submission script template inherited form the Pbs class and then add the following code to the bottom of it
        list_of_job_specific_code = ["# load required modules", "module unload apps/matlab-r2013b", "module load apps/matlab-r2013a", 'echo "Modules loaded:"', "module list\n", "# create the master directory variable", "master=" + wholecell_model_master_dir + "\n", "# create output directory", "base_outDir=" + output_dir + "\n", "# collect the KO combos", "ko_list=" + path_and_name_of_ko_codes, "ko_dir_names=" + path_and_name_of_unique_ko_dir_names + "\n", "# Get all the gene KOs and output folder names", 'for i in `seq 1 ' + str(no_of_unique_ko_sets_per_array_job) + '`', 'do', '    Gene[${i}]=$(awk NR==$((' + str(no_of_unique_ko_sets_per_array_job) + '*(${PBS_ARRAYID}-1)+${i})) ${ko_list})', '    unique_ko_dir_name[${i}]=$(awk NR==$((' + str(no_of_unique_ko_sets_per_array_job) + '*(${PBS_ARRAYID}-1)+${i})) ${ko_dir_names})', "done" + "\n", "# go to master directory", "cd ${master}" + "\n", "# NB have limited MATLAB to a single thread", 'options="-nodesktop -noFigureWindows -nosplash -singleCompThread"' + "\n", "# run 16 simulations in parallel", 'echo "Running simulations (single threaded) in parallel - let\'s start the timer!"', 'start=`date +%s`' + "\n", "# create all the directories for the diarys (the normal output will be all mixed up cause it's in parrallel!)", 'for i in `seq 1 ' + str(no_of_unique_ko_sets_per_array_job) + '`', "do", '    for j in `seq 1 ' + str(no_of_repetitions_of_each_ko) + '`', "    do", '        specific_ko="$(echo ${Gene[${i}]} | sed \'s/{//g\' | sed \'s/}//g\' | sed \"s/\'//g\" | sed \'s/\"//g\' | sed \'s/,/-/g\')/${j}"', '        mkdir -p ${base_outDir}/${unique_ko_dir_name[${i}]}/diary${j}', '        matlab ${options} -r "diary(\'${base_outDir}/${unique_ko_dir_name[${i}]}/diary${j}/diary.out\');addpath(\'${master}\');setWarnings();setPath();runSimulation(\'runner\',\'koRunner\',\'logToDisk\',true,\'outDir\',\'${base_outDir}/${unique_ko_dir_name[${i}]}/${j}\',\'jobNumber\',$((no_of_repetitions_of_each_ko*no_of_unique_ko_sets_per_array_job*(${PBS_ARRAYID}-1)+no_of_unique_ko_sets_per_array_job*(${i}-1)+${j})),\'koList\',{{${Gene[${i}]}}});diary off;exit;" &', "    done", "done", "wait" + "\n", "end=`date +%s`", "runtime=$((end-start))", 'echo "$((${no_of_unique_ko_sets_per_array_job}*${no_of_repetitions_of_each_ko})) simulations took: ${runtime} seconds."']

        # get the standard submission script
        standard_submission_script = self.createSubmissionScriptTemplate(name_of_job, no_of_nodes, no_of_cores, job_array_numbers, walltime, queue_name, outfiles_path, errorfiles_path, "# This script was automatically created by Oliver Chalkley's whole-cell modelling suite. Please contact on o.chalkley@bristol.ac.uk\n")

        self.createStandardSubmissionScript(submission_script_filename, standard_submission_script + list_of_job_specific_code)

        output_dict['submission_script_filename'] = submission_script_filename

        return output_dict

