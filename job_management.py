import os
import sys
sys.path.insert(0, '/home/oli/git/published_libraries/computer_communication_framework')
from computer_communication_framework.base_cluster_submissions import BaseJobSubmission, BaseManageSubmission
import shutil
import time
from concurrent.futures import ProcessPoolExecutor as Pool

class SubmissionKarr2012(BaseJobSubmission):
    """
    This class defines job submissions that work with Oliver Chalkley's whole-cell modelling suite for Karr et al. 2012 Whole-Cell model. It inherits from OliverChalkley's computer_communication_framework.base_cluster_submissions.BaseJobSubmission.
    """

    def __init__(self, submission_name, cluster_connection, ko_name_to_set_dict, queue_name, sim_output_dir, runfiles_path, errorfiles_path, outfiles_path, whole_cell_master_dir, number_of_repetitions_of_each_ko, createAllFilesFunctionName, createDataDictForSpecialistFunctionsFunctionName, createSubmissionScriptFunctionName, createDictOfFileSourceToFileDestinationsFunctionName, first_wait_time = 3600, second_wait_time = 900, temp_storage_path = '/space/oc13378/myprojects/github/uob/wc/mg/oc2/whole_cell_modelling_suite/tmp_storage'):

        # Variables that need to be created by functions because of the base class structure (entered here as None so that they don't get forgotten about)
        BaseJobSubmission.__init__(self, submission_name, cluster_connection, sim_output_dir, errorfiles_path, outfiles_path, runfiles_path, len(ko_name_to_set_dict), number_of_repetitions_of_each_ko, whole_cell_master_dir, temp_storage_path, createAllFilesFunctionName, createDataDictForSpecialistFunctionsFunctionName, createDictOfFileSourceToFileDestinationsFunctionName, createSubmissionScriptFunctionName)
        self.list_of_directories_to_make_on_cluster = None
        self.resource_usage_dict = None
        self.order_of_keys_written_to_file = None
        self.queue_name = queue_name
        self.ko_name_to_set_dict = ko_name_to_set_dict
        self.first_wait_time = first_wait_time
        self.second_wait_time = second_wait_time
        self.createDataDictForAllBespokeFunctions()

    ################# CREATE ALL FILES RELATED FUNCTIONS

    def createAllFilesForKo(self):
        """
        Creates all the files needed for submission: the submission file, the file with all the gene KO codes in and the file with all the names of each KO set in the temporary directory on the local computer.
        """
        ## CREATE THE KO SETS FILE AND THE KO SET NAMES FILE
        ko_code_dict = self.ko_name_to_set_dict.copy()
        ko_code_file_path_and_name = self.submission_data_dict['local_path_and_name_of_ko_codes']
        ko_dir_name_file_path_and_name = self.submission_data_dict['local_path_and_name_of_unique_ko_dir_names']
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
        codes_file = open(ko_code_file_path_and_name, 'wt', encoding='utf-8')
        names_file = open(ko_dir_name_file_path_and_name, 'wt', encoding='utf-8')
        # currently the order of dictionaries in python is only preserved for version 3.6 and does not plan to make that a standard in the future and so for robustness I record the order that the codes and dirs are written to file
        self.order_of_keys_written_to_file = tuple(ko_code_dict.keys())
        for key in self.order_of_keys_written_to_file:
                names_file.write(key + "\n")
                codes_file.write("'" + '\', \''.join(ko_code_dict[key]) + "'\n")

        codes_file.close()
        names_file.close()

        ## CREATE THE SUBMISSION SCRIPT
        self.resource_usage_dict = getattr(self.cluster_connection, self.createSubmissionScriptFunctionName)(self.submission_data_dict.copy())

        # update the submission script name
        self.submission_file_name = os.path.basename(self.resource_usage_dict['submission_script_filename'])
        
        ## CREATE ALL OTHER FILES
        self.createListOfClusterDirectoriesNeeded()
        self.file_source_to_file_dest_dict = self.createDictOfFileSourceToFileDestinations()

        return 

    def createAllFilesForUnittest(self):
        """
        Creates all the files needed for submission: the submission file, the file with all the gene KO codes in and the file with all the names of each KO set in the temporary directory on the local computer.
        """
        ## CREATE THE SUBMISSION SCRIPT
        self.resource_usage_dict = getattr(self.cluster_connection, self.createSubmissionScriptFunctionName)(self.submission_data_dict.copy())

        # update the submission stript name class variable
        self.submission_file_name = os.path.basename(self.resource_usage_dict['submission_script_filename'])
        
        ## CREATE ALL OTHER FILES
        self.createListOfClusterDirectoriesNeeded()
        self.file_source_to_file_dest_dict = self.createDictOfFileSourceToFileDestinations()
        self.order_of_keys_written_to_file = tuple(self.ko_name_to_set_dict.copy().keys())

        return 

    def createListOfClusterDirectoriesNeeded(self):
        self.list_of_directories_to_make_on_cluster = [self.simulation_output_path, self.outfile_path, self.errorfile_path, self.runfiles_path]

        return

    ################# FUNCTIONS RELATED TO CREATING THE SUBMISSION DATA DICT THAT WILL BE USED BY THE BESPOKE FUNCTIONS

    def createDataDictForUnittest(self):
        self.submission_data_dict = {}
        self.submission_data_dict['tmp_save_path'] = self.temp_storage_path
        self.submission_data_dict['name_of_job'] = self.submission_name
        self.submission_data_dict['unittest_master_dir'] = self.master_dir
        self.submission_data_dict['output_dir'] = self.simulation_output_path
        self.submission_data_dict['outfiles_path'] = self.outfile_path + '/' + self.submission_name
        self.submission_data_dict['errorfiles_path'] = self.errorfile_path + '/' + self.submission_name
        self.submission_data_dict['runfiles_path'] = self.runfiles_path
        self.submission_data_dict['no_of_repetitions_of_each_ko'] = self.repetitions_of_unique_task 
        self.submission_data_dict['queue_name'] = self.queue_name
        self.submission_data_dict['no_of_unique_ko_sets'] = len(self.ko_name_to_set_dict)
        self.submission_data_dict['ko_name_to_set_dict'] = self.ko_name_to_set_dict

    def createDataDictForKos(self):
        self.submission_data_dict = {}
        self.submission_data_dict['tmp_save_path'] = self.temp_storage_path
        self.submission_data_dict['name_of_job'] = self.submission_name
        self.submission_data_dict['wholecell_model_master_dir'] = self.master_dir
        self.submission_data_dict['output_dir'] = self.simulation_output_path
        self.submission_data_dict['outfiles_path'] = self.outfile_path
        self.submission_data_dict['errorfiles_path'] = self.errorfile_path
        self.submission_data_dict['runfiles_path'] = self.runfiles_path
        self.submission_data_dict['local_path_and_name_of_ko_codes'] = self.temp_storage_path + '/ko_sets.list'
        self.submission_data_dict['local_path_and_name_of_unique_ko_dir_names'] = self.temp_storage_path + '/ko_set_names.list'
        self.submission_data_dict['path_and_name_of_ko_codes'] = self.runfiles_path + '/ko_sets.list'
        self.submission_data_dict['path_and_name_of_unique_ko_dir_names'] = self.runfiles_path + '/ko_set_names.list'
        self.submission_data_dict['ko_name_to_set_dict'] = self.ko_name_to_set_dict
        self.submission_data_dict['no_of_repetitions_of_each_ko'] = self.repetitions_of_unique_task
        self.submission_data_dict['queue_name'] = self.queue_name

    ############## FUNCTIONS RELATED TO TRANSFERING LOCAL FILES TO THE CLUSTER IN PREPARATION FOR SUBMISSION TO THE CLUSTER

    def createDictOfFileSourceToFileDestinationForKos(self):
        """
        This is a function that could be passed to the createDictOfFileSourceToFileDestinations function in order to transfer all neccessary files from the local disk to the remote cluster for gene knockout simulations.
        """

        output_dict = {self.submission_data_dict['local_path_and_name_of_ko_codes']: self.runfiles_path, self.submission_data_dict['local_path_and_name_of_unique_ko_dir_names']: self.runfiles_path, self.resource_usage_dict['submission_script_filename']: self.runfiles_path}

        return output_dict

    def createDictOfFileSourceToFileDestinationForUnittest(self):
        """
        This is a function that could be passed to the createDictOfFileSourceToFileDestinations function in order to transfer all neccessary files from the local disk to the remote cluster for unittests.
        """

        output_dict = {self.resource_usage_dict['submission_script_filename']: self.runfiles_path}

        return output_dict

class SubmissionManagerKarr2012(BaseManageSubmission):
    """
    This class manages job submissions based on the BaseManageSubmission template that it inherited from but adds functionality that is specific to the Karr 2012 whole-cell moodel.
    """

    def __init__(self, input_tuple):
        (submission_instance, gene_code_to_id_dict, gene_id_to_code_dict, convertDataFunctionName, updateCentralDbFunctionName, functionToGetReleventData, ko_db_path_relative_to_db_connection_flex1, genome_idx_to_id_dict, list_of_states_to_save, ko_library_path_relative_to_db_connection_flex1, static_db_path_relative_to_db_connection_flex1, test_mode) = input_tuple
        BaseManageSubmission.__init__(self, submission_instance, convertDataFunctionName, updateCentralDbFunctionName, test_mode = test_mode)
        self.gene_code_to_id_dict = gene_code_to_id_dict
        self.gene_id_to_code_dict = gene_id_to_code_dict
        self.genome_idx_to_id_dict = genome_idx_to_id_dict
        self.list_of_states_to_save = list_of_states_to_save
        self.functionToGetReleventData = functionToGetReleventData
        self.ko_library_path_relative_to_db_connection_flex1 = ko_library_path_relative_to_db_connection_flex1
        self.ko_db_path_relative_to_db_connection_flex1 = ko_db_path_relative_to_db_connection_flex1
        self.static_db_path_relative_to_db_connection_flex1 = static_db_path_relative_to_db_connection_flex1
        self.simulation_data_dict = {}
        self.data_dict = self.prepareDictForKoDbSubmission()
        self.monitorSubmission(self.submission)
        #super(SubmissionManagerKarr2012, self).__init__(submission_instance, test_mode = test_mode)

    def prepareDictForKoDbSubmission(self):
        """
        This returns a dictionary that provides the structure needed to submit simulation data to the ko.db database.

            data_dict = {

                        'people': 
                                    {'id': None, 'first_name': self.submission.cluster_connection.forename_of_user, 'last_name': self.submission.cluster_connection.surname_of_user, 'user_name': self.submission.cluster_connection.user_name}, 

                        'batchDescription': 
                                    {'id': None, 'name': self.submission.submission_name, 'simulation_initiator_id': None, 'description': 'This batch is automatically generated by Oliver Chalkleys whole-cell modelling suite and has the name: ' + self.submission.submission_name, 'simulation_day': self.submission.time_of_submission['day'], 'simulation_month': self.submission.time_of_submission['month'], 'simulation_year': self.submission.time_of_submission['year'], 'cluster_info': self.submission.cluster_connection.remote_computer_info}, 

                        'koIndex': 
                                    {'id': None, 'number_of_kos': None}, 

                        'simulationDetails': {'id': None, 'ko_index_id': None, 'batch_description_id': None, 'average_growth_rate': None, 'time_when_pinchedDiameter_is_first_zero': None}

                        }
        """

        # initialise dict that KoDb class uses to submit data to the database
        data_dict = {'people': {'id': None, 'first_name': self.submission.cluster_connection.forename_of_user, 'last_name': self.submission.cluster_connection.surname_of_user, 'user_name': self.submission.cluster_connection.user_name}, 'batchDescription': {'id': None, 'name': self.submission.submission_name, 'simulation_initiator_id': None, 'description': 'This batch is automatically generated by Oliver Chalkleys whole-cell modelling suite and has the name: ' + self.submission.submission_name, 'simulation_day': self.submission.time_of_submission['day'], 'simulation_month': self.submission.time_of_submission['month'], 'simulation_year': self.submission.time_of_submission['year'], 'cluster_info': self.submission.cluster_connection.remote_computer_info}, 'koIndex': {'id': None, 'number_of_kos': None}, 'simulationDetails': {'id': None, 'ko_index_id': None, 'batch_description_id': None, 'average_growth_rate': None, 'time_when_pinchedDiameter_is_first_zero': None}}

        return data_dict

    def monitorSubmission(self, submission):
        print("In monitorSubmission!")
        all_outputs_dict = {}
        time.sleep(submission.first_wait_time) # wait 3,600 seconds or 1 hour because definitely nothing will finish in the first hour
        # useful info about the job
        dir_to_ko_set_dict = submission.ko_name_to_set_dict.copy()
        job_resource_allocation_dict = submission.resource_usage_dict.copy()
        print('job_resource_allocation_dict = ', job_resource_allocation_dict)
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
                initial_tuple_of_directory_names = [submission.simulation_output_path + '/' + directory + '/' + str(sub_idx) for job_id in job_array_nos_to_convert for directory in array_no_to_dirs_to_convert_dict[job_id] for sub_idx in submission.resource_usage_dict['list_of_rep_dir_names']]
                # because job arrays go missing and simulation crashes etc we remove all the dirs that don't have a summary.mat
                initial_tuple_of_directory_names = initial_tuple_of_directory_names + missing_jobs.copy()
                missing_jobs = []
                tuple_of_directory_names = []
                for directory_name in initial_tuple_of_directory_names:
                    current_path = directory_name + "/summary.mat"
                    cmds_to_check_file_exists = ['if [ -f ' + current_path + ' ]; then echo "yes";else echo "no";fi']
                    does_file_exist = self.submission.cluster_connection.checkSuccess(self.submission.cluster_connection.sendCommand, cmds_to_check_file_exists)
                    if does_file_exist['stdout'].strip()  == 'yes':
                        tuple_of_directory_names = tuple_of_directory_names + [directory_name]
                    else:
                        missing_jobs = missing_jobs + [directory_name]

                print("tuple_of_directory_names = ", tuple_of_directory_names)
                print("New missing_jobs = ", missing_jobs)
#                tuple_of_directory_names = tuple(tuple_of_directory_names)
                if len(tuple_of_directory_names) > 0:
                    with Pool() as pool:
                        print("converting to pandas!!")
                        list_of_tuples = list(pool.map(self.postSimulationDataProcessing, tuple(zip(tuple_of_directory_names, tuple_of_directory_names)))) # tuple(zip(tuple_of_directory_names, tuple_of_directory_names)) is because the sim and save dir are the same (the functionality is there in case someone wants the option to have different ones though.

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

        # update the KO database
        # convert self.simulation_data_dict from gene codes to gene ids
        simulation_dict = {}
        for ko in self.simulation_data_dict.keys():
            tmp_tuple = tuple([self.gene_code_to_id_dict[code] for code in ko])
            simulation_dict[tmp_tuple] = self.simulation_data_dict[ko]

        # save the final simulation data dict as an insxtance variable and so the update central DB function knows where to look for it
        self.final_simulation_data_dict = simulation_dict.copy()

        # I am temporarily commenting this out because I think the updateCentralDataBase should be called at some other time
        # update central DB 
        self.updateCentralDataBase()

    ############## FUNCTIONS RELATED TO DATA PROCESSING

    def convertTupleOfCodesToGenome(self, tuple_of_codes):
        return tuple([0 if self.gene_id_to_code_dict[self.genome_idx_to_id_dict[idx]] in tuple_of_codes else 1 for idx in range(len(self.genome_idx_to_id_dict))])

    def overallScoreBasic(self, scored_genomes_dict, dict_of_params):
        return {genome: [scored_genomes_dict[genome][-2]] + [(dict_of_params['rawScoreFunc'](scored_genomes_dict[genome][-2]), )] for genome in scored_genomes_dict.keys()}

    def basicGenomeReductionScore(self, simulation_data_dict, dict_of_params):
        # simulation_data_dict = {tuple_of_ids: [(avg_gwth_rate1, division_time1), (avg_gwth_rate2, division_time2), ... , (avg_gwth_rateN, division_timeN)]}
        # want the form ouput_dict = {genome: [(score1, score2, ... , scoreN, (overall_score)]}
        # create dict to convert KO IDs to genomes
        ids_to_genomes_dict = {tuple_of_ids: self.convertTupleOfCodesToGenome(tuple_of_ids) for tuple_of_ids in simulation_data_dict.keys()}
        # create output dictionary and add genomes and individual scores
        scored_genomes = {ids_to_genomes_dict[tuple_of_ids]: [tuple([len(tuple_of_ids) for sim in range(len(simulation_data_dict[tuple_of_ids]))])] + [()] for tuple_of_ids in simulation_data_dict.keys()} # we add an empty tuple here so it is of the same form as fittest_indviduals which means that it is possible to use the same function to score them which makes sense for several reasons

        # add overall score
        output_dict = getattr(self, dict_of_params['overallScoreFuncName'])(scored_genomes, dict_of_params)

        return output_dict

    def createCommandToConvertMatFilesToPickles(self, list_or_dict_of_simdir_and_save_dir):
        list_of_states_to_save = self.list_of_states_to_save.copy()
        if type(list_of_states_to_save) is not list:
               raise ValueError('list_of_states_to_save must be a list of length greater than zero! Here type(list_of_states_to_save) = ', type(list_of_states_to_save))
        if len(list_of_states_to_save) == 0:
            raise ValueError('list_of_states_to_save must be a list of length greater than zero! Here len(list_of_states_to_save) = ', len(list_of_states_to_save))

        # create a dictionary that converts state names to code needed to do that data processing task
        state_name_converter = {'basic_summary': ';extract.saveBasicDetailsAsPickle(list_or_dict_of_simdir_and_save_dir)', 'mature_rna_counts': ';extract.saveMatureRnaCountsAsPickle(list_or_dict_of_simdir_and_save_dir)', 'metabolic_reaction_fluxs': ';extract.saveMetabolicReactionFluxsAsPickle(list_or_dict_of_simdir_and_save_dir)', 'mature_protein_monomer_counts': ';extract.saveMatureProteinMonCountsAsPickle(list_or_dict_of_simdir_and_save_dir)', 'mature_protein_complex_counts': ';extract.saveMatureProteinComCountsAsPickle(list_or_dict_of_simdir_and_save_dir)'}
        # test that all state names given are valid
        if len(set(list_of_states_to_save) - set(state_name_converter.keys())) != 0:
            raise ValueError('list_of_states_to_save must all be valid state names. Here list_of_states_to_save = ', list_of_states_to_save, ' and valid names are ', set(state_name_converter.keys()))

        # create the start  of the command
        cmd_list = self.submission.cluster_connection.activate_virtual_environment_list.copy()
        # create the whole python command in one string and then add to the cmd_list
        python_cmd = 'python -c "import sys;sys.path.insert(0, \'' + self.submission.cluster_connection.path_to_database_dir + '/functions_for_extracting_data_from_matFiles/functions_for_joshuas_matFiles\');import extract_matFile_data_v73 as extract;list_or_dict_of_simdir_and_save_dir = ' + str(list_or_dict_of_simdir_and_save_dir)
        # add the commands needed to save the states requested in list_or_dict_of_simdir_and_save_dir
        for state_name in list_of_states_to_save:
            python_cmd += state_name_converter[state_name]
        # close the double quotes
        python_cmd += '"'
        # add the python_cmd to the cmd_list
        cmd_list += [python_cmd]

        return cmd_list

    def convertMatToPandas(self, tuple_of_sim_and_save_dir):

        # create simdir and save_dir
        list_or_dict_of_simdir_and_save_dir = {}
        list_or_dict_of_simdir_and_save_dir['simdir'] = tuple_of_sim_and_save_dir[0]
        list_or_dict_of_simdir_and_save_dir['save_dir'] = tuple_of_sim_and_save_dir[1]

        # create list of commands
        cmd_list = self.createCommandToConvertMatFilesToPickles(list_or_dict_of_simdir_and_save_dir)

        # submit commands
        convert_data_output_dict = self.submission.cluster_connection.checkSuccess(self.submission.cluster_connection.sendCommand, cmd_list)

        # remove .mat files
        # find mat files
        rm_mats_cmd = self.submission.cluster_connection.activate_virtual_environment_list
        rm_mats_cmd = rm_mats_cmd + ['cd ' + str(list_or_dict_of_simdir_and_save_dir['simdir']), 'python -c "import glob;import os;list_of_matfiles = glob.glob(\'*.mat\');print(list_of_matfiles);print([os.remove(mfile) for mfile in list_of_matfiles])"']
        self.submission.cluster_connection.checkSuccess(self.submission.cluster_connection.sendCommand, rm_mats_cmd)

        # update KO database
        # get simulation info
        tmp_sim_data_dict = self.prepareSimulationDictForKoDbSubmission(list_or_dict_of_simdir_and_save_dir['save_dir'])

        return (convert_data_output_dict, tmp_sim_data_dict,)

    # FUNCTIONS RELATED TO UPDATING THE CENTRAL DB

    def getGrowthAndDivisionTime(self, directory_of_specific_sim_output):
        """
        This returns the average growth and the time when the pinchedDiameter is first zero in a tuple.

        Args:
            directory_of_specific_sim_output (str): Is the absolute path to the simulation output of one particular repetition.

        Returns:
            tuple_of_sim_details (tuple): tuple_of_sim_details[0] is the average growth and tuple_of_sim_details[1] is the time when pinchedDiamter is first zero.
        """

        # in order to name the files so that there is some indication of where they came from (useful when copying loads of files) we get the names of the last two directories that they are saved in which normally says what the batch name is  and what simulation number it is
        dirs_as_list = directory_of_specific_sim_output.split("/")
        sim_name1 = dirs_as_list[-2]
        sim_name2 = dirs_as_list[-1]

        # get the pinch time and average growth rate of this simulation in a tuple
        cmds_to_get_sim_details = self.submission.cluster_connection.activate_virtual_environment_list
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
        required_simulation_data = getattr(self, self.functionToGetReleventData)(directory_of_specific_sim_output)

        # because this is being done in parallel we cannot update the self.simulation_data_dict until the parallel part is complete so we create a temp variable to store it in and pass it back to the create pandas function and then back through to monitor submission function where we are finally out of the  parallel bit and we can update self.simulation_data_dict.
        tmp_sim_data_dict = {}
        if ko_name_to_ko_set_dict[sim_name1] not in tmp_sim_data_dict:
            tmp_sim_data_dict[ko_name_to_ko_set_dict[sim_name1]] = []

        tmp_sim_data_dict[ko_name_to_ko_set_dict[sim_name1]].append(required_simulation_data)

        return tmp_sim_data_dict

    def updateDbGenomeReduction2017(self):
        """
        This function is to update ko.db with regards to genome reduction algorithms for Oliver Chalkley's whole-cell modelling suite.

        Args:
            simulation_dict (dict): A dictionary containing simulation data that needs to be passed to ko.db. The key is a tuple of gene IDs (of the form of IDs in static.db. The value is a list of tuples where each tuple is the average growth and the pinch time for one simulation (there could be multiple simulations of the same KO set which is why this is a list of tuples rather just a tuple i.e. each tuple is the data from one specific simulation).
        """

        # get the all the simulation ddata needed to update the db
        simulation_dict = self.final_simulation_data_dict.copy()
        data_dict = self.data_dict.copy()
        # define variables needed in the python commands
        path_to_ko_db_library = self.submission.cluster_connection.db_connection.path_to_flex1 + '/' + self.ko_library_path_relative_to_db_connection_flex1
        path_to_ko_db = self.submission.cluster_connection.db_connection.path_to_flex1 + '/' + self.ko_db_path_relative_to_db_connection_flex1
        path_to_static_db = self.submission.cluster_connection.db_connection.path_to_flex1 + '/' + self.static_db_path_relative_to_db_connection_flex1
        python_cmds_str = 'import sys;sys.path.insert(0, \'' + path_to_ko_db_library + '\');import ko_db;path_to_ko_data = \'' + path_to_ko_db + '\';path_to_static_db = \'' + path_to_static_db + '\';ko_db_inst = ko_db.KoDb(path_to_ko_data, path_to_static_db);data_dict = ' + str(data_dict) + ';simulation_dict = ' + str(simulation_dict) + ';print(ko_db_inst.addNewSimulations(data_dict, simulation_dict))'
        python_cmds = python_cmds_str.split(";")
        # create a python file and send it to the cluster and execute it and delete old ones
        os.makedirs(self.submission.temp_storage_path)
        # create dir (since it is deleted after the intial simulation is started)
        self.submission.cluster_connection.createLocalFile(self.submission.temp_storage_path + '/update_db_' + self.submission.submission_name + '.py', python_cmds, file_permisions = 700)
        sendFiles_output_dict = self.submission.cluster_connection.checkSuccess(self.submission.cluster_connection.transferFile, self.submission.temp_storage_path + '/update_db_' + self.submission.submission_name + '.py', self.submission.runfiles_path)
        # excute script on the cluster
        cmds_to_update_db = self.submission.cluster_connection.db_connection.activate_virtual_environment_list
        cmds_to_update_db.append('python ' + self.submission.runfiles_path + '/' + 'update_db_' + self.submission.submission_name + '.py')
        print('cmds_to_update_db = ', cmds_to_update_db)
        update_db_out = self.submission.cluster_connection.db_connection.checkSuccess(self.submission.cluster_connection.sendCommand, cmds_to_update_db)
        #all_outputs_dict['update_db_out'] = update_db_out
        if update_db_out['return_code'] != 0:
            raise ValueError('There was an error updating the database!! update_db_out = ', update_db_out)
        else:
            # delete files
            shutil.rmtree('self.temp_storage_path', ignore_errors=True)

        return

