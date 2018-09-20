import time
import stat
import unittest
import sys
sys.path.insert(0, '/space/oc13378/myprojects/github/published_libraries/whole_cell_modelling_suite')
import whole_cell_modelling_suite.connections as connections
import pathlib
import shutil
import os

# because of the abstract nature of the structure we test all everything from only the highest level (youngest generation) classes.

class Karr2012BgTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        ### CREATE INSTANCE OF THE CLASS

        ssh_config_alias = input('Please enter the name in your .ssh/config file that you want to connect to BlueGem with (i.e. the host): ')
        cls.ssh_config_alias = ssh_config_alias
        base_path_on_cluster = input('Please enter a path on the cluster to create unittest directories: ')
        if base_path_on_cluster == '':
            base_path_on_cluster = '/projects/flex1/database/wcm_suite/unittest'
        username = input('Please enter your username on the cluster: ')
        if username == '':
            username = 'oc13378'

        cls.base_path_on_cluster = base_path_on_cluster
        cls.relative_base_that_gets_deleted = 'tests'
        cls.username = username
        cls.forename = 'unit'
        cls.surname = 'test'
        cls.email = 'unit@test.ac.uk'
        cls.output_path = 'output'
        cls.full_output_path = cls.base_path_on_cluster + '/' + cls.relative_base_that_gets_deleted + '/' + cls.output_path
        cls.runfiles_path = 'runfiles'
        cls.full_runfiles_path = cls.base_path_on_cluster + '/' + cls.relative_base_that_gets_deleted + '/' + cls.runfiles_path
        cls.wholecell_model_master = 'WholeCell-master'
        cls.affiliation = 'Test affiliation.'
        bg_conn = connections.Karr2012Bg(cls.username, ssh_config_alias, cls.forename, cls.surname, cls.email, cls.output_path, cls.runfiles_path, cls.wholecell_model_master, affiliation = cls.affiliation)
        cls.bg_conn = bg_conn

        # make remote dirs
        mkdir_cmd = ['mkdir -p ' + cls.base_path_on_cluster + '/' + cls.relative_base_that_gets_deleted + '/' + cls.output_path + ' ' + cls.base_path_on_cluster + '/' + cls.relative_base_that_gets_deleted + '/' + cls.runfiles_path]
        raw_out = cls.bg_conn.checkSuccess(cls.bg_conn.sendCommand, mkdir_cmd)
        if raw_out['return_code'] != 0:
            raise ValueError("Whilst constructing the class we couldn't create remote directories!. raw_out = ", raw_out)

        ### DEFINE LOCAL CLASS VARIABLES NEEDED THROUGHOUT TESTING

        cls.base_dir = 'base_connection_test_directory'
        cls.create_file_path = 'base_connection_test_directory/test_createLocalFile'
        cls.sub_script_dir = 'base_connection_test_directory/submission_script_test'
        cls.move_fname = 'base_connection_test_rsync_remote_transfer_file.txt'
        cls.move_dir1 = 'base_connection_test_directory/test_createLocalFile/test_directory1'
        cls.move_dir2 = 'base_connection_test_directory/test_createLocalFile/test_directory2'
        cls.test_localShellCommand_path = 'base_connection_test_directory/test_localShellCommand'
        cls.test_localShellCommand_file = 'localShellCommand.file'

        ### CREATE DIRS FILES ETC FIR TESTS

        # check that the base connection test directoy doesn't already exist
        if os.path.isdir(cls.base_dir):
            raise ValueError('The directory base_connection_test_directory must not exist, please move some where else.')

        # create directories needed for test
        pathlib.Path(cls.sub_script_dir).mkdir(parents=True, exist_ok=True)
        pathlib.Path(cls.move_dir1).mkdir(parents=True, exist_ok=True)
        pathlib.Path(cls.move_dir2).mkdir(parents=True, exist_ok=True)
        pathlib.Path(cls.test_localShellCommand_path).mkdir(parents=True, exist_ok=True)
        # create a file for transfer tests
        list_of_lines_of_file = ['This', 'is', 'a', 'test']
        list_of_files_to_make = [cls.move_dir1 + "/" + cls.move_fname, cls.test_localShellCommand_path + '/' + cls.test_localShellCommand_file]
        for file_name in list_of_files_to_make:
            with open(file_name, mode = 'wt', encoding = 'utf-8') as myfile:
                for line in list_of_lines_of_file:
                    myfile.write(line + "\n")

    @classmethod
    def tearDownClass(cls):
        print('In tearDownClass!')
        shutil.rmtree(cls.base_dir)
        rm_remote_dirs_cmd = ['rm -r ' + cls.base_path_on_cluster + '/' + cls.relative_base_that_gets_deleted]
        raw_out = cls.bg_conn.checkSuccess(cls.bg_conn.sendCommand, rm_remote_dirs_cmd)
        if raw_out['return_code'] != 0:
            print('Warning, we could not delete the remote files, please do it manually as it may effect future tests. raw_out = ', raw_out)

    ### TEST METHODS

    def test_classCreation(self):
        print('In test_classCreation!')
        self.assertTrue(type(self.bg_conn) == connections.Karr2012Bg)

    # START WITH THE MOST BASE CLASS AND WORK UP

    ################# base_connection.Connection

    def test_ConnectionVariables(self):
        print('In test_ConnectionVariables!')
        results = [self.bg_conn.user_name == self.username, self.bg_conn.ssh_config_alias == self.ssh_config_alias, self.bg_conn.forename_of_user == self.forename, self.bg_conn.surname_of_user == self.surname, self.bg_conn.user_email == self.email, self.bg_conn.affiliation == self.affiliation]

        self.assertTrue(sum(results) == len(results))

    def test_createLocalFile(self):
        print('In test_createLocalFile!')
        # test that a file of thesame name doesn't already exist
        fname = self.create_file_path + '/test_file.txt'
        with pathlib.Path(fname) as test_file:
            if test_file.is_file():
                raise ValueError('This file should not exist - please move it: ', self.fname)

        # create file
        list_of_lines_of_file = ['This', 'is', 'a', 'test']
        self.bg_conn.createLocalFile(fname, list_of_lines_of_file)
        # test file exists
        with pathlib.Path(fname) as test_file:
            self.assertTrue(test_file.is_file())

        # remove the file so similar tests can be done
        os.remove(fname)

    def test_checkLocalFileContents(self):
        print('In test_checkLocalFileContents!') 
        # test that a file of the same name doesn't already exist
        fname = self.create_file_path + '/test_file.txt'
        with pathlib.Path(fname) as test_file:
            if test_file.is_file():
                raise ValueError('This file should not exist - please move it: ', fname)

        # create file
        list_of_lines_of_file = ['This', 'is', 'a', 'test']
        self.bg_conn.createLocalFile(fname, list_of_lines_of_file)
        # check the contents of the file is correct
        with open(fname, 'r') as test_file:
            raw_string = test_file.read().strip()

        list_of_lines = raw_string.split("\n")

        self.assertTrue(list_of_lines_of_file == list_of_lines)

        # remove the file
        os.remove(fname)

    def test_moveFile(self):
        print('In test_moveFile!') 
        # leave remote stuff for a different test class
        # test that a file of thesame name doesn't already exist
        tfile = self.move_fname
        destination = self.base_path_on_cluster + '/' + self.relative_base_that_gets_deleted + '/' + self.output_path
        find_file_cmd = ['if [ -f ' + destination + '/' + tfile + ' ]; then echo yes!; else echo no!; fi']
        raw_out = self.bg_conn.checkSuccess(self.bg_conn.sendCommand, find_file_cmd)
        stdout = raw_out['stdout'].strip()
        if stdout == 'yes!':
            raise ValueError('This file should not exist - please move it: ', self.base_path_on_cluster + '/' + tfile)

        source = self.move_dir1 + "/" + tfile
        # test file exists
        with pathlib.Path(source) as test_file:
            if not test_file.is_file():
                raise ValueError('Transfer file does not exist locally there must have been a problem when constructing the unittest class! test_file.is_file() = ', test_file.is_file())

        self.bg_conn.transferFile(source, destination)
        raw_out = self.bg_conn.checkSuccess(self.bg_conn.sendCommand, find_file_cmd)
        stdout = raw_out['stdout'].strip()
        self.assertTrue(stdout == 'yes!')

        # remove the file so similar tests can be done
        rm_file_cmd = ['rm ' + destination + '/' + tfile]
        raw_out = self.bg_conn.checkSuccess(self.bg_conn.sendCommand, rm_file_cmd)
        if raw_out['return_code'] != 0:
            print('Warning! Remote file may not have been removed! The class tear down should have got rid of it anyway but this may be a sign that something is wrong.')

    def test_remoteConnection(self):
        print('In test_remoteConnection!') 
        ### TWO TESTS. TEST THAT IT RETURNS THE CORRECT KEYS TO THE OUTPUT DICTIONARY AND TEST THAT IT CAN FIND THE CORRECT DIRECTORIES

        # CORRECT DIRECTORIES
        # the only dirs that should be in self.base_path_on_cluster are WholeCell-master and tests
        correct_answer = {'wcms', 'unittest-master', 'WholeCell-master', 'tests'} # we do it in a set just incase things come back in a different order
        cmds = ['ls ' + self.base_path_on_cluster]
        raw_out = self.bg_conn.checkSuccess(self.bg_conn.remoteConnection, cmds)
        output = set(raw_out['stdout'].strip().split("\n"))

        # CORRECT DICTIONARY KEYS
        set_of_raw_out_keys = set(raw_out.keys())
        correct_keys_set = {'stdout', 'stderr', 'return_code'}

        # TEST
        self.assertTrue((output == correct_answer) and (set_of_raw_out_keys == correct_keys_set))

    def test_sendCommand(self):
        print('In test_sendCommand!') 
        ### TWO TESTS. TEST THAT IT RETURNS THE CORRECT KEYS TO THE OUTPUT DICTIONARY AND TEST THAT IT CAN FIND THE CORRECT DIRECTORIES

        # CORRECT DIRECTORIES
        # the only dirs that should be in self.base_path_on_cluster are WholeCell-master and tests
        correct_answer = {'wcms', 'unittest-master', 'WholeCell-master', 'tests'} # we do it in a set just incase things come back in a different order
        cmds = ['ls ' + self.base_path_on_cluster]
        raw_out = self.bg_conn.checkSuccess(self.bg_conn.sendCommand, cmds)
        output = set(raw_out['stdout'].strip().split("\n"))

        # CORRECT DICTIONARY KEYS
        set_of_raw_out_keys = set(raw_out.keys())
        correct_keys_set = {'stdout', 'stderr', 'return_code'}

        # TEST
        self.assertTrue((output == correct_answer) and (set_of_raw_out_keys == correct_keys_set))

    def test_localShellCommand(self):
        print('In test_localShellCommand!') 
        test_cmd = ['ls', self.test_localShellCommand_path]
        raw_out = self.bg_conn.localShellCommand(test_cmd)
        return_code = raw_out[0]
        stdout = raw_out[1].decode('utf-8').strip().split("\n")[0]
        correct_output = self.test_localShellCommand_file
        self.assertTrue((return_code == 0) and (stdout == correct_output))

    ################# base_connection.BaseCluster

    def test_BaseClusterVariables(self):
        print('In test_BaseClusterVariables!') 
        results = [self.bg_conn.remote_computer_info == 'BlueGem: BrisSynBio, Advanced Computing Research Centre, University of Bristol.', self.bg_conn.base_output_path == self.output_path, self.bg_conn.base_runfiles_path == self.runfiles_path, self.bg_conn.submit_command == 'sbatch']

        self.assertTrue(sum(results) == len(results))

    def test_createStandardSubmissionScript(self):
        print('In test_createStandardSubmissionScript!') 
        # create file
        test_code = ['this', 'is', 'a', 'test']
        permissions = '770'
        correct_permissions = '-rwxrwx---'
        fname = self.create_file_path + '/test_submission_file.sh'
        self.bg_conn.createStandardSubmissionScript(fname, test_code, permissions)
        #test file exists
        with pathlib.Path(fname) as test_file:
            file_exist = test_file.is_file()

        # test permissions are correct
        mode = os.stat(fname).st_mode
        returned_perimssions = stat.filemode(mode)

        self.assertTrue((file_exist) and (returned_perimssions == correct_permissions))


    ################# base_connection.BasePbs

    def test_createSubmissionScriptTemplate(self):
        print('In test_createSubmissionScriptTemplate!')
        correct_number_of_lines = 27
        template_script_list = self.bg_conn.createSubmissionScriptTemplate('unittest job name', 1, 1, '1-1', '00:10:00', 'cpu', self.output_path, self.output_path, initial_message_in_code = 'Test initial message', slurm_account_name = 'Flex1')
        correct_types = [type(line) is str for line in template_script_list]

        self.assertTrue((sum(correct_types) == len(correct_types)) and (len(template_script_list) == correct_number_of_lines))

    def test_createStandardSubmissionScriptList(self):
        print('In test_createStandardSubmissionScriptList!') 
        correct_number_of_lines = 25
        task_code = ['sleep 9m', 'echo "This waited 9 minutes and then finished!"']
        template_script_list = self.bg_conn.createStandardSubmissionScriptList(task_code, 'unittest job name', 1, 1, '1-1', '00:10:00', 'cpu', self.full_output_path, self.full_output_path, initial_message_in_code = 'Test initial message', slurm_account_name = 'Flex1')

        self.assertTrue(len(template_script_list) == (correct_number_of_lines + len(task_code)))

    def test_job_submisions_and_job_id_retrieval(self):
        print('In test_job_submisions_and_job_id_retrieval!') 
        # create code
        task_code = ['sleep 1s', 'echo "This waited 1 second and then finished!"']
        template_script_list = self.bg_conn.createStandardSubmissionScriptList(task_code, 'unittest_job_name', 1, 1, '1-2', '00:00:04', 'cpu', self.output_path, self.output_path, initial_message_in_code = '# Test initial message', slurm_account_name = 'Flex1')

        # create submission script
        just_sub_name = 'actual_submission_script.sh'
        fname = self.create_file_path + '/' + just_sub_name
        self.bg_conn.createStandardSubmissionScript(fname, template_script_list)

        # send script to the cluster
        destination = self.base_path_on_cluster + '/' + self.relative_base_that_gets_deleted + '/' + self.runfiles_path
        self.bg_conn.transferFile(fname, destination)

        # submit job to the cluster queue
        submit_cmd = [self.bg_conn.submit_command + ' ' + destination + '/' + just_sub_name]
        raw_submit_out = self.bg_conn.checkSuccess(self.bg_conn.remoteConnection, submit_cmd)

        # collect job ID
        job_id = self.bg_conn.getJobIdFromSubStdOut(raw_submit_out['stdout'].strip().split("\n")[0])
        time.sleep(1)

        # check queue
        raw_queue_out = self.bg_conn.checkQueue(job_id)
        jobs = raw_queue_out['stdout'].strip().split("\n")
        correct_jobs = {'1', '2'}

        self.assertTrue((type(job_id) is int) and (set(jobs) == correct_jobs))


    ############# connections.Karr2012General


    def test_Karr2012GeneralVariables(self):
        print('In test_Karr2012GeneralVariables!') 
        # most of the variables added here are hard coded (as defaults) and so I don't THINK they really need testing
        results = [self.bg_conn.wholecell_master_dir == self.wholecell_model_master]

        self.assertTrue(len(results) == sum(results))

    def test_getGeneInfoDf(self):
        print('In test_getGeneInfoDf!')
        gene_codes = ('MG_001', 'MG_002', 'MG_0001')
        correct_column_names = ('type', 'name', 'symbol', 'functional_unit', 'deletion_phenotype', 'essential_in_model', 'essential_in_experiment')
        info_df = self.bg_conn.getGeneInfoDf(gene_codes)

        self.assertTrue( ( set(info_df.columns) == set(correct_column_names) ) and ( set(info_df.index) == set(gene_codes) ) )

    def test_getAllProteinGroups(self):
        print('In test_getAllProteinGroups!') 
        gene_codes = ('MG_001', 'MG_002', 'MG_0001')
        info_df = self.bg_conn.getGeneInfoDf(gene_codes)
        list_of_protein_groups = self.bg_conn.getAllProteinGroups(info_df, 'MG_001')
        no_of_units = 7
        output_type = list

        self.assertTrue( (type(list_of_protein_groups) is output_type) and (len(list_of_protein_groups) == no_of_units) )

    def test_getNotJr358Genes(self):
        print('In test_getNotJr358Genes!') 
        expected_number_of_codes = 167
        tuple_of_not_jr_358 = self.bg_conn.getNotJr358Genes()
        is_strings = [type(code) == str for code in tuple_of_not_jr_358]

        self.assertTrue( (len(tuple_of_not_jr_358) == expected_number_of_codes) and (len(is_strings) == sum(is_strings)) )
    
    def test_convertGeneCodeToId(self):
        print('In test_convertGeneCodeToId!') 
        gene_code_to_id_dict = self.bg_conn.convertGeneCodeToId(('MG_001', 'MG_002', 'MG_0001'))
        correct_dict = {'MG_001': 1, 'MG_002': 2, 'MG_0001': 297}

        self.assertTrue(gene_code_to_id_dict == correct_dict)


        ############# connections.Karr2012Bg


    def test_createWcmKoScript(self):
        print('In test_createWcmKoScript!') 
        submission_data_dict = {}
        submission_data_dict['tmp_save_path'] = self.create_file_path
        submission_data_dict['name_of_job'] = 'name_of_job'
        submission_data_dict['wholecell_model_master_dir'] = 'wholecell_model_master_dir'
        submission_data_dict['output_dir'] = 'output_dir'
        submission_data_dict['outfiles_path'] = 'outfiles_path'
        submission_data_dict['errorfiles_path'] = 'errorfiles_path'
        submission_data_dict['path_and_name_of_ko_codes'] = 'path_and_name_of_ko_codes'
        submission_data_dict['path_and_name_of_unique_ko_dir_names'] = 'path_and_name_of_unique_ko_dir_names'
        submission_data_dict['ko_name_to_set_dict'] = {'set1': ('MG_001',), 'set2': ('MG_027', 'MG_001')}
        submission_data_dict['no_of_repetitions_of_each_ko'] = 200
        submission_data_dict['queue_name'] = 'cpu'

        output_dict = self.bg_conn.createWcmKoScript(submission_data_dict)
        path_to_file = self.create_file_path + '/' + 'name_of_job_submission.sh'
        correct_dict = {'total_sims': 400, 'no_of_arrays': 2, 'no_of_unique_kos_per_array_job': 1, 'no_of_repetitions_of_each_ko': 200, 'no_of_sims_per_array_job': 200, 'list_of_rep_dir_names': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200], 'submission_script_filename': 'base_connection_test_directory/test_createLocalFile/name_of_job_submission.sh'}
        with pathlib.Path(path_to_file) as test_file:
            self.assertTrue(test_file.is_file() and (output_dict == correct_dict) )

if __name__ == '__main__':
        unittest.main()
