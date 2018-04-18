import sys
sys.path.insert(0, '/home/oli/git/published_libraries/computer_communication_framework')
from computer_communication_framework.base_cluster_submissions import BaseJobSubmission, BaseManageSubmission

class SubmissionKarr2012(BaseJobSubmission):
    """
    This class defines job submissions that work with Oliver Chalkley's whole-cell modelling suite for Karr et al. 2012 Whole-Cell model. It inherits from OliverChalkley's computer_communication_framework.base_cluster_submissions.BaseJobSubmission.
    """

    def __init__(self, submission_name, cluster_connection, ko_name_to_set_dict, simulation_output_path, errorfile_path, outfile_path, runfiles_path, repeitions_of_unique_task, master_dir, updateCentralDbFunction, convertDataFunction, data_conversion_command_code, first_wait_time = 3600, second_wait_time = 900, temp_storage_path = '/space/oc13378/myprojects/github/uob/wc/mg/oc2/whole_cell_modelling_suite/tmp_storage'):

        # Variables that need to be created by functions because of the base class structure (entered here as None so that they don't get forgotten about)
        self.list_of_folders_to_make_on_cluster = None
        self.resource_usage_dict = None
        self.order_of_keys_written_to_file = None

        BaseJobSubmission.__init__(submission_name, cluster_connection, simulation_output_path, errorfile_path, outfile_path, runfiles_path, repeitions_of_unique_task, master_dir, temp_storage_path)

        self.ko_sets_file_name = 'ko_sets.list'
	self.ko_set_names_file_name = 'ko_set_names.list'
	self.ko_name_to_set_dict = ko_name_to_set_dict
	self.ko_set_tmp_storage = self.temp_storage_path + '/' + self.ko_sets_file_name
	self.ko_set_names_tmp_storage = self.temp_storage_path + '/' + self.ko_set_names_file_name
        self.updateCentralDbFunction = updateCentralDbFunction
        self.convertDataFunction = convertDataFunction
        self.data_conversion_command_code = data_conversion_command_code
        self.first_wait_time = first_wait_time
        self.second_wait_time = second_wait_time

    def createAllFiles(self):
        """
        Creates all the files needed for submission: the submission file, the file with all the gene KO codes in and the file with all the names of each KO set in the temporary directory on the local computer.
        """
        ## CREATE THE KO SETS FILE AND THE KO SET NAMES FILE
        ko_code_dict = self.ko_details_dict
        ko_code_file_path_and_name = self.ko_set_tmp_storage
        ko_dir_name_file_path_and_name = self.ko_set_names_tmp_storage
        # check that ko_code_dict has type "dict"
        if type(ko_code_dict) is not dict:
            raise TypeError("ko_code_dict must be a Python dict but here type(ko_code_dict)=%s" %(type(ko_code_dict)))

        # make sure paths exist and if not create them
        # take the file name off the end of both files
        # ko code path
        ko_code_path, ko_code_file = os.path.split(ko_code_file_path_and_name)
        # ko name path
        ko_name_path, ko_name_file = os.path.split(ko_dir_name_file_path_and_name)
        # save codes to the file
        ko_code_file = open(ko_code_file_path_and_name, 'wt', encoding='utf-8')
        ko_name_file = open(ko_dir_name_file_path_and_name, 'wt', encoding='utf-8')
        # currently the order of dictionaries in python is only preserved for version 3.6 and does not plan to make that a standard in the future and so for robustness I record the order that the codes and dirs are written to file
        self.order_of_keys_written_to_file = tuple(ko_code_dict.keys())
        for key in order_of_keys:
                ko_name_file.write(key + "\n")
                ko_code_file.write("'" + '\', \''.join(ko_code_dict[key]) + "'\n")

        ko_code_file.close()
        ko_name_file.close()

        ## CREATE THE SUBMISSION SCRIPT
        self.resource_usage_dict = self.cluster_connection.createWcmKoScript(self.submission_name, self.master_dir, self.simulation_output_path, self.outfile_path, self.errorfile_path, self.ko_set_tmp_storage, self.ko_set_names_tmp_storage, len(self.ko_name_to_set_dict.values()), self.repeitions_of_unique_task, queue_name = 'short')

        return 

    def createListOfClusterDirectoriesNeeded(self):
        self.list_of_folders_to_make_on_cluster = [self.simulation_output_path, self.errorfile_path, self.outfile_path, self.runfiles_path]

        return

    def createDictOfFileSourceToFileDestinations(self):
        output_dict = {self.ko_set_tmp_storage: self.runfiles_path, self.ko_set_names_tmp_storage: self.runfiles_path, self.resource_usage_dict['submission_script_filename']: self.runfiles_path}

        return output_dict

class SubmissionManagerKarr2012(BaseManageSubmission):
    """
    This class manages job submissions based on the BaseManageSubmission template that it inherited from but adds functionality that is specific to the Karr 2012 whole-cell moodel.
    """

    def __init__(self, submission_instance):
        self.data_dict = self.prepareDictForKoDbSubmission()
        BaseManageSubmission.__init__(submission_instance)

    def prepareDictForKoDbSubmission(self):
        """
        This returns a dictionary that provides the structure needed to submit simulation data to the ko.db database.

            data_dict = {

                        'people': 
                                    {'id': None, 'first_name': self.submission.cluster_connection.forename_of_user, 'last_name': self.submission.cluster_connection.surename_of_user, 'user_name': self.submission.cluster_connection.user_name}, 

                        'batchDescription': 
                                    {'id': None, 'name': self.submission.submission_name, 'simulation_initiator_id': None, 'description': 'This batch is automatically generated by Oliver Chalkleys whole-cell modelling suite and has the name: ' + self.submission.submission_name, 'simulation_day': self.submission.time_of_submission['day'], 'simulation_month': self.submission.time_of_submission['month'], 'simulation_year': self.submission.time_of_submission['year'], 'cluster_info': self.submission.cluster_connection.information_about_cluster}, 

                        'koIndex': 
                                    {'id': None, 'number_of_kos': None}, 

                        'simulationDetails': {'id': None, 'ko_index_id': None, 'batch_description_id': None, 'average_growth_rate': None, 'time_when_pinchedDiameter_is_first_zero': None}

                        }
        """

        # initialise dict that KoDb class uses to submit data to the database
        data_dict = {'people': {'id': None, 'first_name': self.submission.cluster_connection.forename_of_user, 'last_name': self.submission.cluster_connection.surename_of_user, 'user_name': self.submission.cluster_connection.user_name}, 'batchDescription': {'id': None, 'name': self.submission.submission_name, 'simulation_initiator_id': None, 'description': 'This batch is automatically generated by Oliver Chalkleys whole-cell modelling suite and has the name: ' + self.submission.submission_name, 'simulation_day': self.submission.time_of_submission['day'], 'simulation_month': self.submission.time_of_submission['month'], 'simulation_year': self.submission.time_of_submission['year'], 'cluster_info': self.submission.cluster_connection.information_about_cluster}, 'koIndex': {'id': None, 'number_of_kos': None}, 'simulationDetails': {'id': None, 'ko_index_id': None, 'batch_description_id': None, 'average_growth_rate': None, 'time_when_pinchedDiameter_is_first_zero': None}}

        return data_dict

    def getGrowthAndDivisionTime(self, directory_of_specific_sim_output):
        """
        This returns the average growth and the time when the pinchedDiameter is first zero in a tuple.

        Args:
            directory_of_specific_sim_output (str): Is the absolute path to the simulation output of one particular repetition.

        Returns:
            tuple_of_sim_details (tuple): tuple_of_sim_details[0] is the average growth and tuple_of_sim_details[1] is the time when pinchedDiamter is first zero.
        """

        # get the pinch time and average growth rate of this simulation in a tuple
        cmds_to_get_sim_details = self.submission.cluster_connection.activate_venv_list
        cmds_to_get_sim_details = cmds_to_get_sim_details + ['cd ' + directory_of_specific_sim_output, 'python -c "import pandas as pd;basic_summary = pd.io.pickle.read_pickle(\'basic_summary_' + sim_name1 + '_' + sim_name2 + '.pickle\');growth_mean = basic_summary[\'metabolicReaction_growth\'].mean();pinch_data = basic_summary[\'geometry_pinchedDiameter\'];pinched_times = list(pinch_data[pinch_data == 0].index);first_pinch = (pinched_times[0] if pinched_times else 0);print(growth_mean);print(first_pinch)"']
        sim_detail_out = self.submission.cluster_connection.checkSuccess(self.submission.cluster_connection.sendCommand, cmds_to_get_sim_details)
        list_of_mgr_and_pinch = sim_detail_out['stdout'].split("\n")
        del list_of_mgr_and_pinch[-1]
        tuple_of_sim_details = (list_of_mgr_and_pinch[0], list_of_mgr_and_pinch[1])

        return tuple_of_sim_details

    def prepareSimulationDictForKoDbSubmission(self, directory_of_specific_sim_output):
        """
        Simulations are performed in parallel and so the data collection of each worker needs to be stored in tmp_sim_data_dict so that all the parallel instances can be added together at the end.

        Args:
            directory_of_specific_sim_output (str): Absolute path to the specifc simulation.
            functionToGetReleventData (function): Is a function that returns the relevant data from this simulation.
            *args: All the arguments needed to pass to functionToGetReleventData.
        """

        # simulation_dict = {('gene_code_1', 'gene_code_2', 'gene_code_3'): [(13, 13446), (17, 14532)], ('gene_code_1', 'gene_code_7', 'gene_code_39', 'gene_code_301'): [(321, 251637), (536127, 36128), (5632, 637)], (34, 432, 12, 19, 234): [(432, 654), (432, 432), (324, 234), (543, 675)]}
        ko_name_to_ko_set_dict = self.submission.ko_name_to_set_dict.copy()
        # the ko name is used as the name of the directory (remember that the last dir name is the repetition number so we want the second last)
        dirs_as_list = directory_of_specific_sim_output.split("/")
        sim_name1 = dirs_as_list[-2]
        sim_name2 = dirs_as_list[-1]

        # because we could perform any kind of in-silico experiments with the whole-cell modelling suite this class needs to be adaptable to collect different data so we require that this method takes a method and it's arguments as an argument so that an algorithm can pick and choose what data it wants to use.
        required_simulation_data = self.submission.functionToGetReleventData(directory_of_specific_sim_output)

        # because this is being done in parallel we cannot update the self.simulation_data_dict until the parallel part is complete so we create a temp variable to store it in and pass it back to the create pandas function and then back through to monitor submission function where we are finally out of the  parallel bit and we can update self.simulation_data_dict.
        tmp_sim_data_dict = {}
        if ko_name_to_ko_set_dict[sim_name1] not in tmp_sim_data_dict:
            tmp_sim_data_dict[ko_name_to_ko_set_dict[sim_name1]] = []

        tmp_sim_data_dict[ko_name_to_ko_set_dict[sim_name1]].append(required_simulation_data)

        return tmp_sim_data_dict

    def monitorSubmission(self, submission):
        print("In monitorSubmission!")
        all_outputs_dict = {}
        time.sleep(submission.first_wait_time) # wait 3,600 seconds or 1 hour because definitely nothing will finish in the first hour
#        time.sleep(15) # this is for debugging
        # useful info about the job
        dir_to_ko_set_dict = submission.ko_name_to_set_dict.copy()
        job_resource_allocation_dict = submission.resource_usage_dict.copy()
        no_of_arrays = job_resource_allocation_dict['no_of_arrays']
        no_of_unique_kos_per_array_job = job_resource_allocation_dict['no_of_unique_kos_per_array_job']
        no_of_repetitions_of_each_ko = job_resource_allocation_dict['no_of_repetitions_of_each_ko']
        # get details about the queue
        queue_output_dict = submission.cluster_connection.checkSuccess(submission.cluster_connection.checkQueue, submission.cluster_job_number)
        stdout_tmp = queue_output_dict['stdout'].split("\n")
        del stdout_tmp[-1]
        # create a list of all the running jobs
        jobs_still_running_list = [int(digit) for digit in stdout_tmp]
        # add a faux job just so it goes round the loop one whole time just in case all the jobs are finished (which they shouldn't but should the unlikely happen I THINK it would be better to get inside the while loop)
        jobs_still_running_list.append(1)
        # need to make sure that we record the data that has been converted so that we don't do it twice
        job_done_dict = {no + 1: False for no in range(no_of_arrays)}
        # keep looping until all the jobs are finished
        missing_jobs = []
        while len(jobs_still_running_list) > 0:
            print("Job array numbers still running: ", jobs_still_running_list)
            # get details about the queue
            queue_output_dict = submission.cluster_connection.checkSuccess(submission.cluster_connection.checkQueue, submission.cluster_job_number)
            stdout_tmp = queue_output_dict['stdout'].split("\n")
            del stdout_tmp[-1]
            jobs_still_running_list = [int(digit) for digit in stdout_tmp]
            # find all array jobs that have completed i.e. make a list of zeros the length of the amount of array jobs then change all zeros to ones that have a job running still. Finding all the zeros in thelist will now give you the array job numbers i.e. if total_list_of_jobs[idx] == 0 then job array idx + 1 has finished.
            total_list_of_jobs = [0] * no_of_arrays
            for idx in jobs_still_running_list:
                total_list_of_jobs[idx-1] = 1

            zero_idxs = [i for i, e in enumerate(total_list_of_jobs) if e == 0]
            finished_array_job_nos = [idx + 1 for idx in zero_idxs]
            print("finished_array_job_nos = ", finished_array_job_nos)
            # remove the jobs that have already had their data converted
            job_array_nos_to_convert = [job for job in finished_array_job_nos if job_done_dict[job] == False]
            print("job_array_nos_to_convert = ", job_array_nos_to_convert)
            # get the dirs corresponding to the arrays
            all_ordered_unique_gene_dirs = submission.order_of_keys_written_to_file
            array_no_to_dirs_to_convert_dict = {}
            for array_job in range(no_of_arrays):
                array_no_to_dirs_to_convert_dict[array_job + 1] = [all_ordered_unique_gene_dirs[no_of_unique_kos_per_array_job*(array_job) + unique_ko_idx] for unique_ko_idx in range(no_of_unique_kos_per_array_job)]
                
            
            # convert data of finished jobs
            if len(job_array_nos_to_convert) > 0:
                # create tuple of dirs (THIS ASSUMES THAT THE MAT DESTINATION IS THE SAME AS THE PANDAS DESTINATION)
                initial_tuple_of_dirs = [submission.simulation_output_path + '/' + dir + '/' + str(sub_idx) for job_id in job_array_nos_to_convert for dir in array_no_to_dirs_to_convert_dict[job_id] for sub_idx in submission.resource_usage_dict['list_of_rep_dir_names']]

                # because job arrays go missing and simulation crashes etc we remove all the dirs that don't have a summary.mat
                initial_tuple_of_dirs = initial_tuple_of_dirs + missing_jobs.copy()
                missing_jobs = []
                tuple_of_dirs = []
                for dir in initial_tuple_of_dirs:
                    current_path = dir + "/summary.mat"
                    cmds_to_check_file_exists = ['if [ -f ' + current_path + ' ]; then echo "yes";else echo "no";fi']
                    does_file_exist = self.submission.cluster_connection.checkSuccess(self.submission.cluster_connection.sendCommand, cmds_to_check_file_exists)
                    if does_file_exist['stdout'].strip()  == 'yes':
                        tuple_of_dirs = tuple_of_dirs + [dir]
                    else:
                        missing_jobs = missing_jobs + [dir]

                print("tuple_of_dirs = ", tuple_of_dirs)
                print("New missing_jobs = ", missing_jobs)
#                tuple_of_dirs = tuple(tuple_of_dirs)
                if len(tuple_of_dirs) > 0:
                    with Pool() as pool:
                        print("converting to pandas!!")
                        list_of_tuples = list(pool.map(self.convertDataToPandas, tuple_of_dirs))

                    [list_of_data_conversion_output_dicts, list_of_tmp_sim_data_dicts] = zip(*list_of_tuples)
                    # update self.simulation_data_dict
                    for idx in range(len(list_of_tmp_sim_data_dicts)):
                        for ko in list_of_tmp_sim_data_dicts[idx].keys(): # this shouldn't be neccessary as there should only be one KO set per dict but we don't know what the code is so resort to looping through the one key
                            if ko not in self.simulation_data_dict:
                                self.simulation_data_dict[ko] = []

                            self.simulation_data_dict[ko] = self.simulation_data_dict[ko] + list_of_tmp_sim_data_dicts[idx][ko]

                # add to job_done_dict
                for arr_no in job_array_nos_to_convert:
                    job_done_dict[arr_no] = True

            time.sleep(submission.second_wait_time) # wait 900 seconds or 15 minutes
            # time.sleep(15) # here for debugging

        # update the KO database
        # convert self.simulation_data_dict from gene codes to gene ids
        simulation_dict = {}
        print("self.simulation_data_dict = ", self.simulation_data_dict)
        for ko in self.simulation_data_dict.keys():
            tmp_tuple = tuple([self.submission.connection.ko_code_to_id_dict[code] for code in ko])
            simulation_dict[tmp_tuple] = self.simulation_data_dict[ko]

        # update central DB
        self.updateCentralDbFunction(simulation_dict)

    def updateDbGenomeReduction(simulation_dict):
        """
        This function is to update ko.db with regards to genome reduction algorithms for Oliver Chalkley's whole-cell modelling suite.

        Args:
            simulation_dict (dict): A dictionary containing simulation data that needs to be passed to ko.db. The key is a tuple of gene IDs (of the form of IDs in static.db. The value is a list of tuples where each tuple is the average growth and the pinch time for one simulation (there could be multiple simulations of the same KO set which is why this is a list of tuples rather just a tuple i.e. each tuple is the data from one specific simulation).
        """

        python_cmds_str = 'import sys;sys.path.insert(0, \'' + self.submission.cluster_connection.db_connection.path_to_flex1 + '/database/ko_db/library\');import ko_db;path_to_ko_data = \'' + self.submission.cluster_connection.db_connection.path_to_flex1 + '/database/ko_db/new_test/ko.db\';path_to_static_db = \'' + self.submission.cluster_connection.db_connection.path_to_flex1 + '/database/staticDB/static.db\';ko_db_inst = ko_db.KoDb(path_to_ko_data, path_to_static_db);data_dict = ' + str(self.data_dict) + ';simulation_dict = ' + str(simulation_dict) + ';print(ko_db_inst.addNewSimulations(data_dict, simulation_dict))'
        python_cmds = python_cmds_str.split(";")
        # create a python file and send it to the cluster and execute it and delete old ones
        os.makedirs(self.submission.temp_storage_path)
        # create dir (since it is deleted after the intial simulation is started)
        self.submission.cluster_connection.createFile(self.submission.temp_storage_path + '/update_db_' + self.submission.submission_name + '.py', python_cmds, file_permisions = 700)
        sendFiles_output_dict = self.submission.cluster_connection.checkSuccess(self.submission.cluster_connection.rsyncFile, self.submission.temp_storage_path + '/update_db_' + self.submission.submission_name + '.py', self.submission.runfiles_path)
        # excute script on the cluster
        cmds_to_update_db = self.submission.cluster_connection.db_connection.activate_venv_list
        cmds_to_update_db.append('python ' + self.submission.runfiles_path + '/' + 'update_db_' + self.submission.submission_name + '.py')
        update_db_out = self.submission.cluster_connection.db_connection.checkSuccess(self.submission.cluster_connection.sendCommand, cmds_to_update_db)
        all_outputs_dict['update_db_out'] = update_db_out
        if update_db_out['return_code'] != 0:
            raise ValueError('There was an error updating the database!! update_db_out = ', update_db_out)
        else:
            # delete files
            shutil.rmtree('self.temp_storage_path', ignore_errors=True)

        return

    def getCommandToConvertDataToPandas(self, list_or_dict_of_simdir_and_save_dir):
        """
        Depending on the in-silico experiement one needs to save different types of data. This command takes an integer number and creates a command to convert the raw simulation data into another form depdnding on the integer.

        Args:
            command_code (int): Integer that tells the function what form you want the data converted into.

        command_code = 
                        1: Save a basic summary, mature RNA counts, mature protein monomer counts, mature protein complex counts and metabolic reaction fluxes.
                        2: Save a basic summary.

        Returns:
            cmd_list (list of strings): Can be passed through the cluster_connection.sendCommand function in order to convert raw simulation data into the requested format. 

        Raises:
            ValueError: If command_code is not a valid number.
        """

        # create the activate virtual environment command
        cmd_list = self.submission.cluster_connection.activate_venv_list
        if self.submission.data_conversion_command_code == 1:
            cmd_list = cmd_list + ['python -c "import sys;sys.path.insert(0, \'' + self.submission.cluster_connection.path_to_database_dir + '/database/functions_for_extracting_data_from_matFiles/functions_for_joshuas_matFiles\');import extract_matFile_data_v73 as extract;list_or_dict_of_simdir_and_save_dir = ' + str(list_or_dict_of_simdir_and_save_dir) + ';extract.saveBasicDetailsAsPickle(list_or_dict_of_simdir_and_save_dir);extract.saveMatureRnaCountsAsPickle(list_or_dict_of_simdir_and_save_dir);extract.saveMetabolicReactionFluxsAsPickle(list_or_dict_of_simdir_and_save_dir);extract.saveMatureProteinComCountsAsPickle(list_or_dict_of_simdir_and_save_dir);extract.saveMatureProteinMonCountsAsPickle(list_or_dict_of_simdir_and_save_dir)"']
        elif self.submission.data_conversion_command_code == 2:
            cmd_list = cmd_list + ['python -c "import sys;sys.path.insert(0, \'' + self.submission.cluster_connection.path_to_database_dir + '/database/functions_for_extracting_data_from_matFiles/functions_for_joshuas_matFiles\');import extract_matFile_data_v73 as extract;list_or_dict_of_simdir_and_save_dir = ' + str(list_or_dict_of_simdir_and_save_dir) + ';extract.saveBasicDetailsAsPickle(list_or_dict_of_simdir_and_save_dir)"']
        else:
            raise ValueError('command_code must be a valid number (1, 2). Here command_code = ', command_code)

        return cmd_list

    def convertDataToPandas(self, directory_s):

        # create simdir and save_dir
        list_or_dict_of_simdir_and_save_dir = {}
        list_or_dict_of_simdir_and_save_dir['simdir'] = directory_s
        list_or_dict_of_simdir_and_save_dir['save_dir'] = directory_s

        # create list of commands
        cmd_list = self.submission.convertDataFunction(list_or_dict_of_simdir_and_save_dir)

        # submit commands
        convert_data_output_dict = self.submission.cluster_connection.checkSuccess(self.submission.cluster_connection.sendCommand, cmd_list)

        # remove .mat files
        # find mat files
        rm_mats_cmd = self.submission.cluster_connection.activate_venv_list
        rm_mats_cmd = rm_mats_cmd + ['cd ' + str(list_or_dict_of_simdir_and_save_dir['simdir']), 'python -c "import glob;import os;list_of_matfiles = glob.glob(\'*.mat\');print(list_of_matfiles);print([os.remove(mfile) for mfile in list_of_matfiles])"']
        self.submission.cluster_connection.checkSuccess(self.submission.cluster_connection.sendCommand, rm_mats_cmd)

        # update KO database
        # get simulation info
        tmp_sim_data_dict = self.prepareSimulationDictForKoDbSubmission(directory_s)

        return (convert_data_output_dict, tmp_sim_data_dict,)
