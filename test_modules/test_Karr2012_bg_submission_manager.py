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

class Karr2012BgManagerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print('Setup starting!')

        ### CREATE INSTANCE OF THE CLASS

        # connection stuff

        ssh_config_alias = input('Please enter the name in your .ssh/config file that you want to connect to BlueCrystal with (i.e. the host): ')
        cls.ssh_config_alias = ssh_config_alias
        base_path_on_cluster = input('Please enter a path on the cluster to create unittest directories: ')
        if base_path_on_cluster == '':
            base_path_on_cluster = '/projects/flex1/database/wcm_suite/unittest'
        test_all_state_conversions = input('Would you like to test converting all the states from mat files to pandas dataframes? (True/False) NOTE: test all the states takes a while (10-15 mins) so don\'t worry if you\'re debugging something completely unrelated don\'t worry about it but it does need to be done every now and then (at least at the end of a change when you think you\'re done and ready to go). ')
        if test_all_state_conversions == '':
            test_all_state_conversions = 'False'
        username = input('Please enter your username on the cluster: ')
        if username == '':
            username = 'oc13378'
        location_of_state_mat_file = input('Please enter the name and location of a state-?.mat file on the local computer (NOTE: This will not be touched as a copy will be made in a temporary directory): ')
        if location_of_state_mat_file == '':
            location_of_state_mat_file = '/home/oli/git/published_libraries/whole_cell_modelling_suite/whole_cell_modelling_suite/test_data/state-20.mat'

        cls.relative_base_that_gets_deleted = 'wcms'
        cls.test_all_state_conversions = eval(test_all_state_conversions)
        cls.location_of_state_mat_file = location_of_state_mat_file
        cls.base_path_on_cluster = base_path_on_cluster
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
        bg_conn = connections.Karr2012Bg(cls.username, ssh_config_alias, cls.forename, cls.surname, cls.email, cls.full_output_path, cls.full_runfiles_path, cls.wholecell_model_master, affiliation = cls.affiliation)
        cls.bg_conn = bg_conn

        # submission stuff

        # the fastest simulating 1ko is MG_107

        cls.fast_ko = 'MG_107'
        cls.submission_name = 'test_submisson'
        cls.ko_name_to_set_dict = {'wcms': (cls.fast_ko,), 'test_sim2': (cls.fast_ko,)}
        cls.repetitions_of_a_unique_simulation = 1
        cls.master_dir = '/projects/flex1/database/WholeCell-master'
        cls.updateCentralDbFunctionName = 'updateCentralDbFunctionTest'
        cls.convertDataFunctionName = 'convertDataFunctionTest'
        cls.data_conversion_command_code = 'data_conversion_command_code_test'
        cls.temp_storage_path = '/home/oli/git/published_libraries/whole-cell-modelling-suite/whole-cell-modelling-suite/temp_storage'
        cls.createDataDictForSpecialistFunctionsFunctionName = 'createDataDictForKos'
        cls.createSubmissionScriptFunctionName = 'createWcmKoScript'
        cls.createDictOfFileSourceToFileDestinationsFunctionName = 'createDictOfFileSourceToFileDestinationForKos'
        cls.createAllFilesFunctionName = 'createAllFilesForKo'
        cls.functionToGetReleventData = 'getGrowthAndDivisionTime'
        cls.queue_name = 'cpu'
        cls.queue_nameUT = 'cpu'

        # CREATE SUBIMSSION INSTANCES
        cls.bg_wcm_ko_sub = job_management.SubmissionKarr2012(cls.submission_name, cls.bg_conn, cls.ko_name_to_set_dict, cls.queue_name, cls.full_output_path, cls.full_runfiles_path, cls.full_out_and_error_files, cls.full_out_and_error_files, cls.master_dir, 1, cls.createAllFilesFunctionName, cls.createDataDictForSpecialistFunctionsFunctionName, cls.createSubmissionScriptFunctionName, cls.createDictOfFileSourceToFileDestinationsFunctionName, first_wait_time = 1, second_wait_time = 1, temp_storage_path = cls.temp_storage_path)

        # CREATE A UNITTEST SUBMISION INSTANCE
        cls.createDataDictForSpecialistFunctionsFunctionNameUT = 'createDataDictForUnittest'
        cls.createSubmissionScriptFunctionNameUT = 'createUnittestScript'
        cls.createDictOfFileSourceToFileDestinationsFunctionNameUT = 'createDictOfFileSourceToFileDestinationForUnittest'
        cls.createAllFilesFunctionNameUT = 'createAllFilesForUnittest'
        cls.getDataForDbFunctionName = 'getGrowthAndDivisionTime'
        quick_list_of_states_to_convert = ['basic_summary']
        long_list_of_states_to_convert = ['basic_summary', 'mature_rna_counts', 'metabolic_reaction_fluxs', 'mature_protein_monomer_counts', 'mature_protein_complex_counts']
        if cls.test_all_state_conversions == True:
            list_of_states_to_convert = long_list_of_states_to_convert.copy()
        else:
            list_of_states_to_convert = quick_list_of_states_to_convert.copy()
        cls.bg_unittest_ko_sub = job_management.SubmissionKarr2012(cls.submission_name, cls.bg_conn, cls.ko_name_to_set_dict, cls.queue_nameUT, cls.full_output_path, cls.full_runfiles_path, cls.full_out_and_error_files, cls.full_out_and_error_files, cls.master_dir, 1, cls.createAllFilesFunctionNameUT, cls.createDataDictForSpecialistFunctionsFunctionNameUT, cls.createSubmissionScriptFunctionNameUT, cls.createDictOfFileSourceToFileDestinationsFunctionNameUT, first_wait_time = 1, second_wait_time = 1, temp_storage_path = cls.temp_storage_path)

        # CREATE A JOB MANAGEMENT INSTANCE IN TEST MODE
        cls.test_manager = job_management.SubmissionManagerKarr2012(cls.bg_unittest_ko_sub, cls.updateCentralDbFunctionName, cls.convertDataFunctionName, cls.getDataForDbFunctionName, list_of_states_to_save = list_of_states_to_convert, ko_db_path_relative_to_db_connection_flex1 = 'database/ko_db/unittest_ko_db/unittest_ko.db', test_mode = True)

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
        # create a file for transfer tests
        list_of_lines_of_file = ['This', 'is', 'a', 'test']
        list_of_files_to_make = [cls.move_dir1 + "/" + cls.move_fname, cls.test_localShellCommand_path + '/' + cls.test_localShellCommand_file]
        for file_name in list_of_files_to_make:
            with open(file_name, mode = 'wt', encoding = 'utf-8') as myfile:
                for line in list_of_lines_of_file:
                    myfile.write(line + "\n")

        ### CREATE REMOTE DIRECTORY THAT GETS DELETED EVERYTIME
        mkdir_cmd = ['mkdir -p ' + cls.base_path_on_cluster + '/' + cls.relative_base_that_gets_deleted]
        raw_out = cls.bg_conn.checkSuccess(cls.bg_conn.sendCommand, mkdir_cmd)
        if raw_out['return_code'] != 0:
            print("Warning, could not create the remote dir. This currently shouldn't cause an error but may do later on. raw_out = ", raw_out)

        # make remote dirs
        cls.tmp_mat_files = 'example_simulation'
        cls.full_path_to_sim_example = cls.base_path_on_cluster + '/' + cls.relative_base_that_gets_deleted + '/' + cls.tmp_mat_files
        mkdir_cmd = ['mkdir -p ' + cls.full_path_to_sim_example]
        raw_out = cls.bg_conn.checkSuccess(cls.bg_conn.sendCommand, mkdir_cmd)
        if raw_out['return_code'] != 0:
            raise ValueError("Whilst constructing the class we couldn't create remote directories!. raw_out = ", raw_out)

        # also add a whole simulation there
        source_path = '/projects/flex1/database/mat_files/version73_example_mats_files/1/' # put the trailing slash so that it only copies the contents of the dir
        transfer_cmd = ['rsync -aP ' + source_path + ' ' + cls.full_path_to_sim_example]
        raw_out = cls.bg_conn.checkSuccess(cls.bg_conn.sendCommand, transfer_cmd)
        if raw_out['return_code'] != 0:
            raise ValueError("Could not transfer example simulation data to the temporary directory! raw_out = ", raw_out)

        print('Setup up finishing!')

    @classmethod
    def tearDownClass(cls):
        print('In tearDownClass!')
        shutil.rmtree(cls.base_dir)
        shutil.rmtree(cls.temp_storage_path)
        rm_remote_dirs_cmd = ['rm -r ' + cls.base_path_on_cluster + '/' + cls.relative_base_that_gets_deleted]
        raw_out = cls.bg_conn.checkSuccess(cls.bg_conn.sendCommand, rm_remote_dirs_cmd)
        if raw_out['return_code'] != 0:
            print('Warning, we could not delete the remote files, please do it manually as it may effect future tests. raw_out = ', raw_out)

    ### TEST METHODS

    def test_classCreation(self):
        print('test_classCreation')
        self.assertTrue(type(self.test_manager) is job_management.SubmissionManagerKarr2012)

    # START WITH THE MOST BASE CLASS AND WORK UP

    ################# base_cluster_submission.BaseJobSubmission

    def test_BaseTestJobManagementVariables(self):
        print('test_BaseTestJobManagementVariables')
        test_submission_time = {'day': 8, 'month': 1, 'year': 2018}
        actual_submission_time = self.test_manager.submission.time_of_submission.copy()
        submission_time_test_result = (test_submission_time == actual_submission_time)

        # the data dict gets created by calling the relevant function. This means that if there is a problem with the function then this will not be wright so I will not create a unittest for that function.
        test_data_dict = {'people': {'id': None, 'first_name': self.test_manager.submission.cluster_connection.forename_of_user, 'last_name': self.test_manager.submission.cluster_connection.surname_of_user, 'user_name': self.test_manager.submission.cluster_connection.user_name}, 'batchDescription': {'id': None, 'name': self.test_manager.submission.submission_name, 'simulation_initiator_id': None, 'description': 'This batch is automatically generated by Oliver Chalkleys whole-cell modelling suite and has the name: ' + self.test_manager.submission.submission_name, 'simulation_day': self.test_manager.submission.time_of_submission['day'], 'simulation_month': self.test_manager.submission.time_of_submission['month'], 'simulation_year': self.test_manager.submission.time_of_submission['year'], 'cluster_info': self.test_manager.submission.cluster_connection.remote_computer_info}, 'koIndex': {'id': None, 'number_of_kos': None}, 'simulationDetails': {'id': None, 'ko_index_id': None, 'batch_description_id': None, 'average_growth_rate': None, 'time_when_pinchedDiameter_is_first_zero': None}}
        actual_data_dict = self.test_manager.data_dict.copy()
        data_dict_test_result = (actual_data_dict == test_data_dict)

        self.assertTrue(submission_time_test_result and data_dict_test_result)

    def test_createCommandToConvertMatFilesToPicklesUT(self):
        print('In test_createCommandToConvertMatFilesToPickles!')
        # the correct command list
        if self.test_all_state_conversions == True:
            actual_cmd = ['module add apps/anaconda3-2.3.0', 'source activate whole_cell_modelling_suite', 'python -c "import sys;sys.path.insert(0, \'/projects/flex1/database/functions_for_extracting_data_from_matFiles/functions_for_joshuas_matFiles\');import extract_matFile_data_v73 as extract;list_or_dict_of_simdir_and_save_dir = /projects/flex1/database/wcm_suite/unittest/wcms/tmp_sim;extract.saveBasicDetailsAsPickle(list_or_dict_of_simdir_and_save_dir);extract.saveMatureRnaCountsAsPickle(list_or_dict_of_simdir_and_save_dir);extract.saveMetabolicReactionFluxsAsPickle(list_or_dict_of_simdir_and_save_dir);extract.saveMatureProteinMonCountsAsPickle(list_or_dict_of_simdir_and_save_dir);extract.saveMatureProteinComCountsAsPickle(list_or_dict_of_simdir_and_save_dir)"']
        else:
            actual_cmd = ['module add apps/anaconda3-2.3.0', 'source activate whole_cell_modelling_suite', 'python -c "import sys;sys.path.insert(0, \'/projects/flex1/database/functions_for_extracting_data_from_matFiles/functions_for_joshuas_matFiles\');import extract_matFile_data_v73 as extract;list_or_dict_of_simdir_and_save_dir = /projects/flex1/database/wcm_suite/unittest/wcms/tmp_sim;extract.saveBasicDetailsAsPickle(list_or_dict_of_simdir_and_save_dir)"']

        # create path to state-?.mat file
        filename = self.location_of_state_mat_file.split('/')[-1]
        path = self.tmp_local_data_storage_path
        # create the command
        cmd_to_test = self.test_manager.createCommandToConvertMatFilesToPickles('/projects/flex1/database/wcm_suite/unittest/wcms/tmp_sim')

        self.assertTrue(cmd_to_test == actual_cmd)

    def test_convertMatToPandasUT(self):
        # This simultaneously tests getGrowthAndDivisionTime and prepareSimulationDictForKoDbSubmission so won't bother maing anoother two functions to do that

        print('In test_convertMatToPandasUT!')
        # start by creating a copy of the example simulation data
        # create destination path
        source_path_list = self.full_path_to_sim_example.split('/')
        destination_path = source_path_list[:-1].copy()
        destination_path = '/'.join(destination_path)
        destination_path = destination_path + '/tmp_sim'

        copy_cmd = ['rsync -aP ' + self.full_path_to_sim_example + '/ ' + destination_path]
        raw_out = self.bg_conn.checkSuccess(self.bg_conn.sendCommand, copy_cmd)
        if raw_out['return_code'] != 0:
            raise ValueError("Whilst constructing the class we couldn't create remote directories!. raw_out = ", raw_out)

        convert_data_output_dict, tmp_sim_data_dict = self.test_manager.convertMatToPandas(destination_path, destination_path)

        template_tmp_sim_data_dict =  {('MG_107',): [('1.68143350439e-05', '0')]}

        self.assertTrue(template_tmp_sim_data_dict == tmp_sim_data_dict)

        return

    def test_updateDbGenomeReduction2017(self):
        print('In test_updateDbGenomeReduction2017!')
        # make sure that the untitest DB is empty by deleting the existing one and creating a new one
        clear_db_cmd = ['cd /projects/flex1/database/ko_db/unittest_ko_db; rm unittest_ko.db; sqlite3 unittest_ko.db < unittest_ko_db.schema']
        test_db_cmd = ["echo $'.headers on\n.mode columns\nselect simulationDetails.time_when_pinchedDiameter_is_first_zero, simulationDetails.average_growth_rate, koIndex.number_of_kos, batchDescription.name, people.last_name, people.user_name from simulationDetails join koIndex on simulationDetails.ko_index_id = koIndex.id join batchDescription on simulationDetails.batch_description_id = batchDescription.id join people on people.id = batchDescription.simulation_initiator_id;' > tmp_sql.sqlite; sqlite3 /projects/flex1/database/ko_db/unittest_ko_db/unittest_ko.db < tmp_sql.sqlite; rm tmp_sql.sqlite"]
        raw_out = self.bg_conn.checkSuccess(self.bg_conn.sendCommand, clear_db_cmd)
        if raw_out['return_code'] != 0:
            raise ValueError('Could not create a fresh unittest database". raw_out = ', raw_out)
        
        pathlib.Path(self.bg_unittest_ko_sub.temp_storage_path).mkdir(parents=True, exist_ok=True)
        outs =  self.bg_unittest_ko_sub.prepareForSubmission()
        self.test_manager.final_simulation_data_dict =  {('111',): [('1.68143350439e-05', '0')]} # monitorSubmission function converts from gene codes to IDs before updatng the DB. Because we can't run monitorSubmission here we just change the code to idea. Here MG_107 = 111.
        list_of_return_codes = [output['return_code'] for output in outs]
        if sum(list_of_return_codes) > 0:
            raise ValueError('There has been a problem preparing some jobs for submission. The return codes from JobSubmission.prepareForSubmission() are: ', list_of_return_codes, '. The submission file name is ', self.submission.submission_file_name, ' and the temp_storage_path was ', self.submission.temp_storage_path)

        raw_out1 = self.bg_conn.checkSuccess(self.bg_conn.sendCommand, test_db_cmd)
        raw_out1_test = {'return_code': 0, 'stdout': '', 'stderr': None}
        self.test_manager.updateDbGenomeReduction2017()
        raw_out2 = self.bg_conn.checkSuccess(self.bg_conn.sendCommand, test_db_cmd)
        raw_out2_test = {'return_code': 0, 'stdout': 'time_when_pinchedDiameter_is_first_zero  average_growth_rate  number_of_kos  name            last_name   user_name \n---------------------------------------  -------------------  -------------  --------------  ----------  ----------\n0                                        1.68143350439e-05    1              test_submisson  test        oc13378   \n', 'stderr': None}

        self.assertTrue( (raw_out1 == raw_out1_test) and (raw_out2 == raw_out2_test) )

if __name__ == '__main__':
        unittest.main()

