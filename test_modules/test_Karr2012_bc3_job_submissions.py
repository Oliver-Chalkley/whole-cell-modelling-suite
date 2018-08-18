import time
import stat
import unittest
import sys
sys.path.insert(0, '/home/oli/git/published_libraries/whole_cell_modelling_suite')
import whole_cell_modelling_suite.connections as connections
import whole_cell_modelling_suite.job_management as job_management
import pathlib
import shutil
import os
import numbers

class Karr2012Bc3JobsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        ### CREATE INSTANCE OF THE CLASS

        # connection stuff

        ssh_config_alias = input('Please enter the name in your .ssh/config file that you want to connect to BlueCrystal Phase III with (i.e. the host): ')
        cls.ssh_config_alias = ssh_config_alias
        base_path_on_cluster = input('Please enter a path on the cluster to create unittest directories: ')
        if base_path_on_cluster == '':
            base_path_on_cluster = '/panfs/panasas01/bluegem-flex1/database/wcm_suite/unittest'
        username = input('Please enter your username on the cluster: ')
        if username == '':
            username = 'oc13378'

        cls.base_path_on_cluster = base_path_on_cluster
        cls.relative_base_that_gets_deleted = 'wcms'
        cls.username = username
        cls.forename = 'unit'
        cls.surname = 'test'
        cls.email = 'unit@test.ac.uk'
        cls.output_path = 'output'
        cls.full_output_path = cls.base_path_on_cluster + '/' + cls.relative_base_that_gets_deleted + '/' + cls.output_path
        cls.runfiles_path = 'runfiles'
        cls.full_runfiles_path = cls.base_path_on_cluster + '/' + cls.relative_base_that_gets_deleted + '/' + cls.runfiles_path
        cls.out_and_error_files = 'out_and_error_files'
        cls.full_out_and_error_files = cls.base_path_on_cluster + '/' + cls.relative_base_that_gets_deleted + '/' + cls.out_and_error_files
        cls.wholecell_model_master = 'WholeCell-master'
        cls.affiliation = 'Test affiliation.'
        bc3_conn = connections.Karr2012Bc3(cls.username, ssh_config_alias, cls.forename, cls.surname, cls.email, cls.full_output_path, cls.full_runfiles_path, cls.wholecell_model_master, affiliation = cls.affiliation)
        cls.bc3_conn = bc3_conn

        # submission stuff

        # the fastest simulating 1ko is MG_107

        cls.fast_ko = 'MG_107'
        cls.submission_name = 'test_submisson'
        cls.ko_name_to_set_dict = {'wcms': (cls.fast_ko,), 'test_sim2': (cls.fast_ko,)}
        cls.repetitions_of_a_unique_simulation = 1
        cls.master_dir = '/panfs/panasas01/emat/oc13378/WholeCell/wc/mg/WholeCell-master'
        cls.updateCentralDbFunctionName = 'updateCentralDbFunctionTest'
        cls.convertDataFunctionName = 'convertDataFunctionTest'
        cls.getDataForDbFunctionName = 'getGrowthAndDivisionTime'
        cls.temp_storage_path = '/home/oli/git/published_libraries/whole-cell-modelling-suite/whole-cell-modelling-suite/temp_storage'
        cls.createDataDictForSpecialistFunctionsFunctionName = 'createDataDictForKos'
        cls.createSubmissionScriptFunctionName = 'createWcmKoScript'
        cls.createDictOfFileSourceToFileDestinationsFunctionName = 'createDictOfFileSourceToFileDestinationForKos'
        cls.createAllFilesFunctionName = 'createAllFilesForKo'
        cls.queue_name = 'short'
        cls.queue_nameUT = 'testq'

        # CREATE SUBIMSSION INSTANCES
        cls.bc3_wcm_ko_sub = job_management.SubmissionKarr2012(cls.submission_name, cls.bc3_conn, cls.ko_name_to_set_dict, cls.queue_name, cls.full_output_path, cls.full_runfiles_path, cls.full_out_and_error_files, cls.full_out_and_error_files, cls.master_dir, 1, cls.createAllFilesFunctionName, cls.createDataDictForSpecialistFunctionsFunctionName, cls.createSubmissionScriptFunctionName, cls.createDictOfFileSourceToFileDestinationsFunctionName, first_wait_time = 1, second_wait_time = 1, temp_storage_path = cls.temp_storage_path)

        # CREATE A UNITTEST SUBMISION INSTANCE
        cls.createDataDictForSpecialistFunctionsFunctionNameUT = 'createDataDictForUnittest'
        cls.createSubmissionScriptFunctionNameUT = 'createUnittestScript'
        cls.createDictOfFileSourceToFileDestinationsFunctionNameUT = 'createDictOfFileSourceToFileDestinationForUnittest'
        cls.createAllFilesFunctionNameUT = 'createAllFilesForUnittest'
        quick_list_of_states_to_convert = ['basic_summary']
        long_list_of_states_to_convert = ['basic_summary', 'mature_rna_counts', 'metabolic_reaction_fluxs', 'mature_protein_monomer_counts', 'mature_protein_complex_counts']
        cls.bc3_unittest_ko_sub = job_management.SubmissionKarr2012(cls.submission_name, cls.bc3_conn, cls.ko_name_to_set_dict, cls.queue_nameUT, cls.full_output_path, cls.full_runfiles_path, cls.full_out_and_error_files, cls.full_out_and_error_files, cls.master_dir, 1, cls.createAllFilesFunctionNameUT, cls.createDataDictForSpecialistFunctionsFunctionNameUT, cls.createSubmissionScriptFunctionNameUT, cls.createDictOfFileSourceToFileDestinationsFunctionNameUT, first_wait_time = 1, second_wait_time = 1, temp_storage_path = cls.temp_storage_path)

        ### DEFINE LOCAL CLASS VARIABLES NEEDED THROUGHOUT TESTING

        cls.base_dir = 'base_connection_test_directory'
        cls.create_file_path = 'base_connection_test_directory/test_createLocalFile'
        cls.sub_script_dir = 'base_connection_test_directory/submission_script_test'
        cls.move_fname = 'base_connection_test_rsync_remote_transfer_file.txt'
        cls.move_dir1 = 'base_connection_test_directory/test_createLocalFile/test_directory1'
        cls.move_dir2 = 'base_connection_test_directory/test_createLocalFile/test_directory2'
        cls.test_localShellCommand_path = 'base_connection_test_directory/test_localShellCommand'
        cls.test_localShellCommand_file = 'localShellCommand.file'
        cls.tmp_local_data_storage_path = 'base_connection_test_directory/local_data_storage'

        ### CREATE DIRS FILES ETC FIR TESTS

        # check that the base connection test directoy doesn't already exist
        if os.path.isdir(cls.base_dir):
            raise ValueError('The directory base_connection_test_directory must not exist, please move some where else.')

        # create directories needed for test
        pathlib.Path(cls.sub_script_dir).mkdir(parents=True, exist_ok=True)
        pathlib.Path(cls.move_dir1).mkdir(parents=True, exist_ok=True)
        pathlib.Path(cls.move_dir2).mkdir(parents=True, exist_ok=True)
        pathlib.Path(cls.test_localShellCommand_path).mkdir(parents=True, exist_ok=True)
        pathlib.Path(cls.tmp_local_data_storage_path).mkdir(parents=True, exist_ok=True)

        # create a copy of the state-?.mat file in the temp directory
        cls.bc3_conn.transferFile(cls.location_of_state_mat_file, cls.tmp_local_data_storage_path, remote = False)

        # create a file for transfer tests
        list_of_lines_of_file = ['This', 'is', 'a', 'test']
        list_of_files_to_make = [cls.move_dir1 + "/" + cls.move_fname, cls.test_localShellCommand_path + '/' + cls.test_localShellCommand_file]
        for file_name in list_of_files_to_make:
            with open(file_name, mode = 'wt', encoding = 'utf-8') as myfile:
                for line in list_of_lines_of_file:
                    myfile.write(line + "\n")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.base_dir)
        shutil.rmtree(cls.temp_storage_path)
        rm_remote_dirs_cmd = ['rm -r ' + cls.base_path_on_cluster + '/' + cls.relative_base_that_gets_deleted]
        raw_out = cls.bc3_conn.checkSuccess(cls.bc3_conn.sendCommand, rm_remote_dirs_cmd)
        if raw_out['return_code'] != 0:
            print('Warning, we could not delete the remote files, please do it manually as it may effect future tests. raw_out = ', raw_out)

    ### TEST METHODS

    def test_classCreation(self):
        print('In test_classCreation!')
        self.assertTrue(type(self.bc3_wcm_ko_sub) == job_management.SubmissionKarr2012)

    # START WITH THE MOST BASE CLASS AND WORK UP

    ################# base_cluster_submission.BaseJobSubmission

    def test_BaseJobSubmissionVariables(self):
        print('In test_BaseJobSubmissionVariables!')
        results = [self.bc3_wcm_ko_sub.submission_name == self.submission_name, self.bc3_wcm_ko_sub.submission_file_name == None, self.bc3_wcm_ko_sub.temp_storage_path == self.temp_storage_path + '/' + self.bc3_wcm_ko_sub.unique_job_name, type(self.bc3_wcm_ko_sub.unique_job_name) is str, self.bc3_wcm_ko_sub.cluster_connection == self.bc3_conn, self.bc3_wcm_ko_sub.simulation_output_path == self.full_output_path, self.bc3_wcm_ko_sub.outfile_path == self.full_out_and_error_files, self.bc3_wcm_ko_sub.errorfile_path == self.full_out_and_error_files, self.bc3_wcm_ko_sub.runfiles_path == self.full_runfiles_path, self.bc3_wcm_ko_sub.cluster_job_number is None, self.bc3_wcm_ko_sub.time_of_submission is None]

        self.assertTrue(sum(results) == len(results))

    # ALL THE PARENT METHODS REQUIRE CHILD METHODS AND SO WE JUMP TO THE CHILD AND THEN GO BACK TO THE PARENT METHODS

    def test_SubmissionKarr2012Variables(self):
        print('In test_SubmissionKarr2012Variables!')
        results = [self.bc3_wcm_ko_sub.list_of_directories_to_make_on_cluster is None, self.bc3_wcm_ko_sub.resource_usage_dict is None, self.bc3_wcm_ko_sub.order_of_keys_written_to_file is None, self.bc3_wcm_ko_sub.queue_name == self.queue_name, self.bc3_wcm_ko_sub.ko_name_to_set_dict == self.ko_name_to_set_dict, self.bc3_wcm_ko_sub.createDataDictForSpecialistFunctionsFunctionName == self.createDataDictForSpecialistFunctionsFunctionName, self.bc3_wcm_ko_sub.createSubmissionScriptFunctionName == self.createSubmissionScriptFunctionName, self.bc3_wcm_ko_sub.first_wait_time == 1, self.bc3_wcm_ko_sub.second_wait_time == 1]

        self.assertTrue(sum(results) == len(results))

    def test_createListOfClusterDirectoriesNeeded(self):
        print('In test_createListOfClusterDirectoriesNeeded!')
        self.bc3_wcm_ko_sub.createListOfClusterDirectoriesNeeded()
        self.assertTrue(self.bc3_wcm_ko_sub.list_of_directories_to_make_on_cluster == [self.bc3_wcm_ko_sub.simulation_output_path, self.bc3_wcm_ko_sub.outfile_path, self.bc3_wcm_ko_sub.errorfile_path, self.bc3_wcm_ko_sub.runfiles_path])

    def test_createAllFiles_and_createDictOfFileSourceToFileDestinations(self):
        print('In test_createAllFiles_and_createDictOfFileSourceToFileDestinations!')
        self.bc3_wcm_ko_sub.createAllFiles()
        correct_dict = {self.bc3_wcm_ko_sub.submission_data_dict['local_path_and_name_of_ko_codes']: self.bc3_wcm_ko_sub.runfiles_path, self.bc3_wcm_ko_sub.submission_data_dict['local_path_and_name_of_unique_ko_dir_names']: self.bc3_wcm_ko_sub.runfiles_path, self.bc3_wcm_ko_sub.resource_usage_dict['submission_script_filename']: self.bc3_wcm_ko_sub.runfiles_path}

        file_exists = []
        for local_file in self.bc3_wcm_ko_sub.file_source_to_file_dest_dict:
            with pathlib.Path(local_file) as test_file:
                file_exists.append(test_file.is_file())

        self.assertTrue( ( correct_dict == self.bc3_wcm_ko_sub.file_source_to_file_dest_dict ) and ( len(file_exists) == sum(file_exists) ) )

    def test_createUniqueJobName(self):
        print('In test_createUniqueJobName!')
        unique_name = [self.bc3_wcm_ko_sub.createUniqueJobName('test_') for i in range(2)]
        self.assertTrue(unique_name[0] != unique_name[1])

    def test_prepareForSubmission(self):
        print('In test_prepareForSubmission!')
        list_of_output_dicts = self.bc3_wcm_ko_sub.prepareForSubmission()
        correct_return_codes = [individual_dict['return_code'] == 0 for individual_dict in list_of_output_dicts]

        self.assertTrue( len(correct_return_codes) == sum(correct_return_codes) )

#    def test_createCommandToConvertMatFilesToPickles(self):
#        print('In test_createCommandToConvertMatFilesToPickles!!')
#        test_dir = '/test/dir'
#        #cmd_list = self.bc3_wcm_ko_sub.createCommandToConvertMatFilesToPickles(test_dir)
#        print('cmd_list = ', cmd_list)
#        self.assertTrue(False)

    def test_submitJobToCluster(self):
        print('In test_submitJobToCluster!')
        # check that no job number has been assigned to this instance yet
        pre_sub_job_no_check = self.bc3_wcm_ko_sub.cluster_job_number == None
        # check that no time of submission has been assigned to this instance yet
        pre_sub_sub_time_check = self.bc3_wcm_ko_sub.time_of_submission == None
        # submit job to the cluster
        list_of_output_dicts = self.bc3_wcm_ko_sub.prepareForSubmission()
        self.bc3_wcm_ko_sub.submitJobToCluster()
        
        # check that job number has been assigned to this instance 
        job_no_check = type(self.bc3_wcm_ko_sub.cluster_job_number) is int
        # check that no time of submission has been assigned to this instance yet
        sub_time_check = type(self.bc3_wcm_ko_sub.time_of_submission) is dict

        # clean up files/jobs
#        os.remove(self.bc3_unittest_ko_sub.resource_usage_dict['submission_script_filename'])
        cancel_job_cmd = ['qdel ' + str(self.bc3_wcm_ko_sub.cluster_job_number) + '[]']
        raw_out = self.bc3_wcm_ko_sub.cluster_connection.checkSuccess(self.bc3_wcm_ko_sub.cluster_connection.remoteConnection, cancel_job_cmd)
        if raw_out['return_code'] != 0:
                print('WARNING: This did not cancel the job submission!')

        self.assertTrue(pre_sub_job_no_check and pre_sub_sub_time_check and job_no_check and sub_time_check)


    ################### BECAUSE THE WCM TAKES SO LONG WE WANT TO TEST JOB SUBMISSION WITH A SHORT UNITTEST VERSION FOR USE WITH THE NEXT CLASS BUT NEEDS TO BE SET UP FROM HERE

    ### TEST METHODS

    def test_classCreationUT(self):
        print('In test_classCreationUT!')
        self.assertTrue(type(self.bc3_unittest_ko_sub) == job_management.SubmissionKarr2012)

    # START WITH THE MOST BASE CLASS AND WORK UP

    ################# base_cluster_submission.BaseJobSubmission

    def test_BaseJobSubmissionVariablesUT(self):
        print('In test_BaseJobSubmissionVariablesUT!')
        results = [self.bc3_unittest_ko_sub.submission_name == self.submission_name, self.bc3_unittest_ko_sub.submission_file_name == None, self.bc3_unittest_ko_sub.temp_storage_path == self.temp_storage_path + '/' + self.bc3_unittest_ko_sub.unique_job_name, type(self.bc3_unittest_ko_sub.unique_job_name) is str, self.bc3_unittest_ko_sub.cluster_connection == self.bc3_conn, self.bc3_unittest_ko_sub.simulation_output_path == self.full_output_path, self.bc3_unittest_ko_sub.outfile_path == self.full_out_and_error_files, self.bc3_unittest_ko_sub.errorfile_path == self.full_out_and_error_files, self.bc3_unittest_ko_sub.runfiles_path == self.full_runfiles_path, self.bc3_unittest_ko_sub.cluster_job_number is None, self.bc3_unittest_ko_sub.time_of_submission is None]

        self.assertTrue(sum(results) == len(results))

    # ALL THE PARENT METHODS REQUIRE CHILD METHODS AND SO WE JUMP TO THE CHILD AND THEN GO BACK TO THE PARENT METHODS

    def test_SubmissionKarr2012VariablesUT(self):
        print('In test_SubmissionKarr2012VariablesUT!')
        results = [self.bc3_unittest_ko_sub.list_of_directories_to_make_on_cluster is None, self.bc3_unittest_ko_sub.resource_usage_dict is None, self.bc3_unittest_ko_sub.order_of_keys_written_to_file is None, self.bc3_unittest_ko_sub.queue_name == self.queue_nameUT, self.bc3_unittest_ko_sub.ko_name_to_set_dict == self.ko_name_to_set_dict, self.bc3_unittest_ko_sub.createDataDictForSpecialistFunctionsFunctionName == self.createDataDictForSpecialistFunctionsFunctionNameUT, self.bc3_unittest_ko_sub.createSubmissionScriptFunctionName == self.createSubmissionScriptFunctionNameUT, self.bc3_unittest_ko_sub.first_wait_time == 1, self.bc3_unittest_ko_sub.second_wait_time == 1]

        self.assertTrue(sum(results) == len(results))

    def test_createListOfClusterDirectoriesNeededUT(self):
        print('In test_createListOfClusterDirectoriesNeededUT!')
        self.bc3_unittest_ko_sub.createListOfClusterDirectoriesNeeded()
        self.assertTrue(self.bc3_unittest_ko_sub.list_of_directories_to_make_on_cluster == [self.bc3_unittest_ko_sub.simulation_output_path, self.bc3_unittest_ko_sub.outfile_path, self.bc3_unittest_ko_sub.errorfile_path, self.bc3_unittest_ko_sub.runfiles_path])

    def test_createAllFiles_and_createDictOfFileSourceToFileDestinationsUT(self):
        print('In test_createAllFiles_and_createDictOfFileSourceToFileDestinationsUT!')
        self.bc3_unittest_ko_sub.createAllFiles()
        correct_dict = {self.bc3_unittest_ko_sub.resource_usage_dict['submission_script_filename']: self.bc3_unittest_ko_sub.runfiles_path}

        file_exists = []
        for local_file in self.bc3_unittest_ko_sub.file_source_to_file_dest_dict.keys():
            with pathlib.Path(local_file) as test_file:
                file_exists.append(test_file.is_file())

        # clean up files
        for local_file in self.bc3_unittest_ko_sub.file_source_to_file_dest_dict.keys():
            os.remove(local_file)
        self.assertTrue( ( correct_dict == self.bc3_unittest_ko_sub.file_source_to_file_dest_dict ) and ( len(file_exists) == sum(file_exists) ) )

    def test_createUniqueJobNameUT(self):
        print('In test_createUniqueJobNameUT!')
        unique_name = [self.bc3_unittest_ko_sub.createUniqueJobName('test_') for i in range(2)]
        self.assertTrue(unique_name[0] != unique_name[1])

    def test_prepareForSubmissionUT(self):
        print('In test_prepareForSubmissionUT!')
        list_of_output_dicts = self.bc3_unittest_ko_sub.prepareForSubmission()
        correct_return_codes = [individual_dict['return_code'] == 0 for individual_dict in list_of_output_dicts]

        # clean up files
        os.remove(self.bc3_unittest_ko_sub.resource_usage_dict['submission_script_filename'])

        self.assertTrue( len(correct_return_codes) == sum(correct_return_codes) )

    def test_submitJobToClusterUT(self):
        print('In test_submitJobToClusterUT!')
        # check that no job number has been assigned to this instance yet
        pre_sub_job_no_check = self.bc3_unittest_ko_sub.cluster_job_number == None
        # check that no time of submission has been assigned to this instance yet
        pre_sub_sub_time_check = self.bc3_unittest_ko_sub.time_of_submission == None
        # submit job to the cluster
        list_of_output_dicts = self.bc3_unittest_ko_sub.prepareForSubmission()
        self.bc3_unittest_ko_sub.submitJobToCluster()
        
        # check that job number has been assigned to this instance 
        job_no_check = type(self.bc3_unittest_ko_sub.cluster_job_number) is int
        # check that no time of submission has been assigned to this instance yet
        sub_time_check = type(self.bc3_unittest_ko_sub.time_of_submission) is dict

        # clean up files/jobs
#        os.remove(self.bc3_unittest_ko_sub.resource_usage_dict['submission_script_filename'])
        cancel_job_cmd = ['qdel ' + str(self.bc3_unittest_ko_sub.cluster_job_number) + '[]']
        raw_out = self.bc3_unittest_ko_sub.cluster_connection.checkSuccess(self.bc3_unittest_ko_sub.cluster_connection.remoteConnection, cancel_job_cmd)
        if raw_out['return_code'] != 0:
                print('WARNING: This did not cancel the job submission!')


        self.assertTrue(pre_sub_job_no_check and pre_sub_sub_time_check and job_no_check and sub_time_check)


if __name__ == '__main__':
        unittest.main()

