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

class Karr2012BgRealManageTest(unittest.TestCase):
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
        cls.repetitions_of_a_unique_simulation = 3
        cls.master_dir = '/projects/flex1/database/WholeCell-master'
        cls.updateCentralDbFunctionName = 'updateDbGenomeReduction2017'
        cls.convertDataFunctionName = 'convertMatToPandas'
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
        cls.bg_wcm_ko_sub = job_management.SubmissionKarr2012(cls.submission_name, cls.bg_conn, cls.ko_name_to_set_dict, cls.queue_name, cls.full_output_path, cls.full_runfiles_path, cls.full_out_and_error_files, cls.full_out_and_error_files, cls.master_dir, cls.repetitions_of_a_unique_simulation, cls.createAllFilesFunctionName, cls.createDataDictForSpecialistFunctionsFunctionName, cls.createSubmissionScriptFunctionName, cls.createDictOfFileSourceToFileDestinationsFunctionName, first_wait_time = 15, second_wait_time = 15, temp_storage_path = cls.temp_storage_path)

        # CREATE A UNITTEST SUBMISION INSTANCE
        cls.master_dir = '/projects/flex1/database/wcm_suite/unittest/unittest-master'
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
        cls.bg_unittest_ko_sub = job_management.SubmissionKarr2012(cls.submission_name, cls.bg_conn, cls.ko_name_to_set_dict, cls.queue_nameUT, cls.full_output_path, cls.full_runfiles_path, cls.full_out_and_error_files, cls.full_out_and_error_files, cls.master_dir, cls.repetitions_of_a_unique_simulation, cls.createAllFilesFunctionNameUT, cls.createDataDictForSpecialistFunctionsFunctionNameUT, cls.createSubmissionScriptFunctionNameUT, cls.createDictOfFileSourceToFileDestinationsFunctionNameUT, first_wait_time = 1, second_wait_time = 1, temp_storage_path = cls.temp_storage_path)

        # CREATE A JOB MANAGEMENT INSTANCE IN TEST MODE
        #cls.test_manager = job_management.SubmissionManagerKarr2012(cls.bg_unittest_ko_sub, cls.convertDataFunctionName, cls.updateCentralDbFunctionName, cls.getDataForDbFunctionName, list_of_states_to_save = list_of_states_to_convert, ko_db_path_relative_to_db_connection_flex1 = 'database/ko_db/unittest_ko_db/unittest_ko.db', test_mode = True)

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

    def getJr358Genes(self):
            """The function returns the 358 genes that Joshua Rees classified for potential KOs."""
            return ('MG_001', 'MG_003', 'MG_004', 'MG_005', 'MG_006', 'MG_007', 'MG_008', 'MG_009', 'MG_012', 'MG_013', 'MG_014', 'MG_015', 'MG_019', 'MG_020', 'MG_021', 'MG_022', 'MG_023', 'MG_026', 'MG_027', 'MG_029', 'MG_030', 'MG_031', 'MG_033', 'MG_034', 'MG_035', 'MG_036', 'MG_037', 'MG_038', 'MG_039', 'MG_040', 'MG_041', 'MG_042', 'MG_043', 'MG_044', 'MG_045', 'MG_046', 'MG_047', 'MG_048', 'MG_049', 'MG_050', 'MG_051', 'MG_052', 'MG_053', 'MG_055', 'MG_473', 'MG_058', 'MG_059', 'MG_061', 'MG_062', 'MG_063', 'MG_064', 'MG_065', 'MG_066', 'MG_069', 'MG_070', 'MG_071', 'MG_072', 'MG_073', 'MG_075', 'MG_077', 'MG_078', 'MG_079', 'MG_080', 'MG_081', 'MG_082', 'MG_083', 'MG_084', 'MG_085', 'MG_086', 'MG_087', 'MG_088', 'MG_089', 'MG_090', 'MG_091', 'MG_092', 'MG_093', 'MG_094', 'MG_097', 'MG_098', 'MG_099', 'MG_100', 'MG_101', 'MG_102', 'MG_476', 'MG_104', 'MG_105', 'MG_106', 'MG_107', 'MG_109', 'MG_110', 'MG_111', 'MG_112', 'MG_113', 'MG_114', 'MG_118', 'MG_119', 'MG_120', 'MG_121', 'MG_122', 'MG_123', 'MG_124', 'MG_126', 'MG_127', 'MG_128', 'MG_130', 'MG_132', 'MG_136', 'MG_137', 'MG_139', 'MG_141', 'MG_142', 'MG_143', 'MG_145', 'MG_149', 'MG_150', 'MG_151', 'MG_152', 'MG_153', 'MG_154', 'MG_155', 'MG_156', 'MG_157', 'MG_158', 'MG_159', 'MG_160', 'MG_161', 'MG_162', 'MG_163', 'MG_164', 'MG_165', 'MG_166', 'MG_167', 'MG_168', 'MG_169', 'MG_170', 'MG_171', 'MG_172', 'MG_173', 'MG_174', 'MG_175', 'MG_176', 'MG_177', 'MG_178', 'MG_179', 'MG_180', 'MG_181', 'MG_182', 'MG_183', 'MG_184', 'MG_186', 'MG_187', 'MG_188', 'MG_189', 'MG_190', 'MG_191', 'MG_192', 'MG_194', 'MG_195', 'MG_196', 'MG_197', 'MG_198', 'MG_200', 'MG_201', 'MG_203', 'MG_204', 'MG_205', 'MG_206', 'MG_208', 'MG_209', 'MG_210', 'MG_481', 'MG_482', 'MG_212', 'MG_213', 'MG_214', 'MG_215', 'MG_216', 'MG_217', 'MG_218', 'MG_221', 'MG_224', 'MG_225', 'MG_226', 'MG_227', 'MG_228', 'MG_229', 'MG_230', 'MG_231', 'MG_232', 'MG_234', 'MG_235', 'MG_236', 'MG_238', 'MG_239', 'MG_240', 'MG_244', 'MG_245', 'MG_249', 'MG_250', 'MG_251', 'MG_252', 'MG_253', 'MG_254', 'MG_257', 'MG_258', 'MG_259', 'MG_261', 'MG_262', 'MG_498', 'MG_264', 'MG_265', 'MG_266', 'MG_270', 'MG_271', 'MG_272', 'MG_273', 'MG_274', 'MG_275', 'MG_276', 'MG_277', 'MG_278', 'MG_282', 'MG_283', 'MG_287', 'MG_288', 'MG_289', 'MG_290', 'MG_291', 'MG_292', 'MG_293', 'MG_295', 'MG_297', 'MG_298', 'MG_299', 'MG_300', 'MG_301', 'MG_302', 'MG_303', 'MG_304', 'MG_305', 'MG_309', 'MG_310', 'MG_311', 'MG_312', 'MG_315', 'MG_316', 'MG_317', 'MG_318', 'MG_321', 'MG_322', 'MG_323', 'MG_324', 'MG_325', 'MG_327', 'MG_329', 'MG_330', 'MG_333', 'MG_334', 'MG_335', 'MG_517', 'MG_336', 'MG_339', 'MG_340', 'MG_341', 'MG_342', 'MG_344', 'MG_345', 'MG_346', 'MG_347', 'MG_349', 'MG_351', 'MG_352', 'MG_353', 'MG_355', 'MG_356', 'MG_357', 'MG_358', 'MG_359', 'MG_361', 'MG_362', 'MG_363', 'MG_522', 'MG_365', 'MG_367', 'MG_368', 'MG_369', 'MG_370', 'MG_372', 'MG_375', 'MG_376', 'MG_378', 'MG_379', 'MG_380', 'MG_382', 'MG_383', 'MG_384', 'MG_385', 'MG_386', 'MG_387', 'MG_390', 'MG_391', 'MG_392', 'MG_393', 'MG_394', 'MG_396', 'MG_398', 'MG_399', 'MG_400', 'MG_401', 'MG_402', 'MG_403', 'MG_404', 'MG_405', 'MG_407', 'MG_408', 'MG_409', 'MG_410', 'MG_411', 'MG_412', 'MG_417', 'MG_418', 'MG_419', 'MG_421', 'MG_424', 'MG_425', 'MG_426', 'MG_427', 'MG_428', 'MG_429', 'MG_430', 'MG_431', 'MG_433', 'MG_434', 'MG_435', 'MG_437', 'MG_438', 'MG_442', 'MG_444', 'MG_445', 'MG_446', 'MG_447', 'MG_448', 'MG_451', 'MG_453', 'MG_454', 'MG_455', 'MG_457', 'MG_458', 'MG_460', 'MG_462', 'MG_463', 'MG_464', 'MG_465', 'MG_466', 'MG_467', 'MG_468', 'MG_526', 'MG_470')

    def getDictOfJr358Codes(self, conn):
            """
            Creates a dictionary whos keys are Joshua Rees 358 gene codes and values are the gene ID acording to our database.
            """

            # get joshua rees' 358 gene codes
            jr358_codes = self.getJr358Genes()
            # create bg connection in order to access the staticDB which is the official source of our codes and IDs etc
    #	bgConn = bg('oc13378', 'bg', '/users/oc13378/.ssh/uob/uob-rsa')
            # use staticDB to create the dictionary
            code2id_dict = conn.db_connection.convertGeneCodeToId(jr358_codes)

            return code2id_dict

    ### TEST METHODS

    def test_monitorSubmission(self):
        print('test_monitorSubmission')
        clear_db_cmd = ['cd /projects/flex1/database/ko_db/unittest_ko_db; rm unittest_ko.db; sqlite3 unittest_ko.db < unittest_ko_db.schema']
        raw_out = self.bg_conn.checkSuccess(self.bg_conn.sendCommand, clear_db_cmd)
        if raw_out['return_code'] != 0:
            raise ValueError('Could not create a fresh unittest database". raw_out = ', raw_out)
        
        gene_code_to_id_dict = self.getDictOfJr358Codes(self.bg_conn)
        test_manager = job_management.SubmissionManagerKarr2012(self.bg_wcm_ko_sub, gene_code_to_id_dict, self.convertDataFunctionName, self.updateCentralDbFunctionName, self.getDataForDbFunctionName, ko_db_path_relative_to_db_connection_flex1 = 'database/ko_db/unittest_ko_db/unittest_ko.db', test_mode = False)
        test_db_cmd = ['sqlite3 /projects/flex1/database/ko_db/unittest_ko_db/unittest_ko.db "select count(simulationDetails.average_growth_rate) from simulationDetails join koIndex on simulationDetails.ko_index_id = koIndex.id join batchDescription on simulationDetails.batch_description_id = batchDescription.id join people on people.id = batchDescription.simulation_initiator_id"']
        raw_out = self.bg_conn.checkSuccess(self.bg_conn.sendCommand, test_db_cmd)
        raw_out_correct = {'stderr': None, 'return_code': 0, 'stdout': '6\n'}
        print('raw_out_correct = ', raw_out_correct)
        print('raw_out = ', raw_out)
        self.assertTrue( (type(test_manager) is job_management.SubmissionManagerKarr2012) and (raw_out_correct == raw_out) )

if __name__ == '__main__':
        unittest.main()

