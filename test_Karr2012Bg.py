import time
import stat
import unittest
import connections
import pathlib
import shutil
import os

# because of the abstract nature of the structure we test all everything from only the highest level (youngest generation) classes.

class Karr2012BgTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        ### CREATE INSTANCE OF THE CLASS

        ssh_config_alias = input('Please enter the name in your .ssh/config file that you want to connect to (i.e. the host): ')
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
        shutil.rmtree(cls.base_dir)
        rm_remote_dirs_cmd = ['rm -r ' + cls.base_path_on_cluster + '/' + cls.relative_base_that_gets_deleted]
        raw_out = cls.bg_conn.checkSuccess(cls.bg_conn.sendCommand, rm_remote_dirs_cmd)
        if raw_out['return_code'] != 0:
            print('Warning, we could not delete the remote files, please do it manually as it may effect future tests. raw_out = ', raw_out)

    ### TEST METHODS

    def test_classCreation(self):
        self.assertTrue(type(self.bg_conn) == connections.Karr2012Bg)

    # START WITH THE MOST BASE CLASS AND WORK UP

    ################# base_connection.Connection

    def test_ConnectionVariables(self):
        results = [self.bg_conn.user_name == self.username, self.bg_conn.ssh_config_alias == self.ssh_config_alias, self.bg_conn.forename_of_user == self.forename, self.bg_conn.surname_of_user == self.surname, self.bg_conn.user_email == self.email, self.bg_conn.affiliation == self.affiliation]

        self.assertTrue(sum(results) == len(results))

    def test_createLocalFile(self):
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
        ### TWO TESTS. TEST THAT IT RETURNS THE CORRECT KEYS TO THE OUTPUT DICTIONARY AND TEST THAT IT CAN FIND THE CORRECT DIRECTORIES

        # CORRECT DIRECTORIES
        # the only dirs that should be in self.base_path_on_cluster are WholeCell-master and tests
        correct_answer = {'WholeCell-master', 'tests'} # we do it in a set just incase things come back in a different order
        cmds = ['ls ' + self.base_path_on_cluster]
        raw_out = self.bg_conn.checkSuccess(self.bg_conn.remoteConnection, cmds)
        output = set(raw_out['stdout'].strip().split("\n"))

        # CORRECT DICTIONARY KEYS
        set_of_raw_out_keys = set(raw_out.keys())
        correct_keys_set = {'stdout', 'stderr', 'return_code'}

        # TEST
        self.assertTrue((output == correct_answer) and (set_of_raw_out_keys == correct_keys_set))

    def test_sendCommand(self):
        ### TWO TESTS. TEST THAT IT RETURNS THE CORRECT KEYS TO THE OUTPUT DICTIONARY AND TEST THAT IT CAN FIND THE CORRECT DIRECTORIES

        # CORRECT DIRECTORIES
        # the only dirs that should be in self.base_path_on_cluster are WholeCell-master and tests
        correct_answer = {'WholeCell-master', 'tests'} # we do it in a set just incase things come back in a different order
        cmds = ['ls ' + self.base_path_on_cluster]
        raw_out = self.bg_conn.checkSuccess(self.bg_conn.sendCommand, cmds)
        output = set(raw_out['stdout'].strip().split("\n"))

        # CORRECT DICTIONARY KEYS
        set_of_raw_out_keys = set(raw_out.keys())
        correct_keys_set = {'stdout', 'stderr', 'return_code'}

        # TEST
        self.assertTrue((output == correct_answer) and (set_of_raw_out_keys == correct_keys_set))

    def test_localShellCommand(self):
        test_cmd = ['ls', self.test_localShellCommand_path]
        raw_out = self.bg_conn.localShellCommand(test_cmd)
        return_code = raw_out[0]
        stdout = raw_out[1].decode('utf-8').strip().split("\n")[0]
        correct_output = self.test_localShellCommand_file
        self.assertTrue((return_code == 0) and (stdout == correct_output))

    ################# base_connection.BaseCluster

    def test_BaseClusterVariables(self):
        results = [self.bg_conn.remote_computer_info == 'BlueGem: BrisSynBio, Advanced Computing Research Centre, University of Bristol.', self.bg_conn.base_output_path == self.output_path, self.bg_conn.base_runfiles_path == self.runfiles_path, self.bg_conn.submit_command == 'sbatch']

        self.assertTrue(sum(results) == len(results))

    def test_createStandardSubmissionScript(self):
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
        correct_number_of_lines = 26
        template_script_list = self.bg_conn.createSubmissionScriptTemplate('unittest job name', 1, 1, '1-1', '00:10:00', 'cpu', self.output_path, self.output_path, initial_message_in_code = 'Test initial message', slurm_account_name = 'Flex1')
        correct_types = [type(line) is str for line in template_script_list]

        self.assertTrue((sum(correct_types) == len(correct_types)) and (len(template_script_list) == correct_number_of_lines))

    def test_createStandardSubmissionScriptList(self):
        correct_number_of_lines = 24
        task_code = ['sleep 9m', 'echo "This waited 9 minutes and then finished!"']
        template_script_list = self.bg_conn.createStandardSubmissionScriptList(task_code, 'unittest job name', 1, 1, '1-1', '00:10:00', 'cpu', self.full_output_path, self.full_output_path, initial_message_in_code = 'Test initial message', slurm_account_name = 'Flex1')

        self.assertTrue(len(template_script_list) == (correct_number_of_lines + len(task_code)))

    def test_job_submisions_and_job_id_retrieval(self):
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


if __name__ == '__main__':
        unittest.main()
