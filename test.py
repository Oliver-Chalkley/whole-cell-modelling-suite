import unittest
import connections
import pathlib
import shutil
import os
#import numbers
#from pathlib import Path

# because of the abstract nature of the structure we test all everything from only the highest level (youngest generation) classes.

class Karr2012Bc3KosTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        ### CREATE INSTANCE OF THE CLASS

        ssh_config_alias = input('Please enter the name in your .ssh/config file that you want to connect to (i.e. the host): ')
        cls.ssh_config_alias = ssh_config_alias
        base_path_on_cluster = input('Please enter a path on the cluster to create unittest directories: ')
        if base_path_on_cluster == '':
            base_path_on_cluster = '/panfs/panasas01/bluegem-flex1/database/wcm_suite/unittest'

        cls.base_path_on_cluster = base_path_on_cluster
        cls.username = 'ut1'
        cls.forename = 'unit'
        cls.surname = 'test'
        cls.email = 'unit@test.ac.uk'
        cls.output_path = 'output'
        cls.runfiles_path = 'runfiles'
        cls.wholecell_model_master = 'WholeCell-master'
        cls.affiliation = 'Test affiliation.'
        bc3_conn = connections.Karr2012Bc3Kos(cls.username, ssh_config_alias, cls.forename, cls.surname, cls.email, cls.output_path, cls.runfiles_path, cls.wholecell_model_master, affiliation = cls.affiliation)
        cls.bc3_conn = bc3_conn

        # make remote dirs
        mkdir_cmd = ['mkdir -p ' + cls.base_path_on_cluster + '/' + cls.output_path + ' ' + cls.base_path_on_cluster + '/' + cls.runfiles_path]

        ### DEFINE LOCAL CLASS VARIABLES NEEDED THROUGHOUT TESTING

        cls.base_dir = 'base_connection_test_directory'
        cls.create_file_path = 'base_connection_test_directory/test_createLocalFile'
        cls.sub_script_dir = 'base_connection_test_directory/submission_script_test'
        cls.move_fname = 'base_connection_test_rsync_remote_transfer_file.txt'
        cls.move_dir1 = 'base_connection_test_directory/test_createLocalFile/test_directory1'
        cls.move_dir2 = 'base_connection_test_directory/test_createLocalFile/test_directory2'

        ### CREATE DIRS FILES ETC FIR TESTS

        # check that the base connection test directoy doesn't already exist
        if os.path.isdir(cls.base_dir):
            raise ValueError('The directory base_connection_test_directory must not exist, please move some where else.')

        # create directories needed for test
        pathlib.Path(cls.sub_script_dir).mkdir(parents=True, exist_ok=True)
        pathlib.Path(cls.move_dir1).mkdir(parents=True, exist_ok=True)
        pathlib.Path(cls.move_dir2).mkdir(parents=True, exist_ok=True)
        # create a file for transfer tests
        list_of_lines_of_file = ['This', 'is', 'a', 'test']
        with open(cls.move_dir1 + "/" + cls.move_fname, mode = 'wt', encoding = 'utf-8') as myfile:
            for line in list_of_lines_of_file:
                myfile.write(line + "\n")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.base_dir)

    ### TEST METHODS

    def test_classCreation(self):
        self.assertTrue(type(self.bc3_conn) == connections.Karr2012Bc3Kos)

    # START WITH THE MOST BASE CLASS AND WORK UP

    # base_connection.Connection
    def test_ConnectionVariables(self):
        results = [self.bc3_conn.user_name == self.username, self.bc3_conn.ssh_config_alias == self.ssh_config_alias, self.bc3_conn.forename_of_user == self.forename, self.bc3_conn.surname_of_user == self.surname, self.bc3_conn.user_email == self.email, self.bc3_conn.affiliation == self.affiliation]

        self.assertTrue(sum(results) == len(results))

    def test_createLocalFile(self):
        # test that a file of thesame name doesn't already exist
        fname = self.create_file_path + '/test_file.txt'
        with pathlib.Path(fname) as test_file:
            if test_file.is_file():
                raise ValueError('This file should not exist - please move it: ', self.fname)

        # create file
        list_of_lines_of_file = ['This', 'is', 'a', 'test']
        self.bc3_conn.createLocalFile(fname, list_of_lines_of_file)
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
        self.bc3_conn.createLocalFile(fname, list_of_lines_of_file)
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
        destination = self.base_path_on_cluster + '/' + self.output_path
        find_file_cmd = ['if [ -f ' + destination + '/' + tfile + ' ]; then echo yes!; else echo no!; fi']
        raw_out = self.bc3_conn.checkSuccess(self.bc3_conn.sendCommand, find_file_cmd)
        stdout = raw_out['stdout'].strip()
        print("raw1 = ", raw_out)
        if stdout == 'yes!':
            raise ValueError('This file should not exist - please move it: ', self.base_path_on_cluster + '/' + tfile)

        source = self.move_dir1 + "/" + tfile
        print('source = ', source)
        print('destination = ', destination)
        # test file exists
        with pathlib.Path(source) as test_file:
            print('file exists locally: ', test_file.is_file())
        self.bc3_conn.transferFile(source, destination)
        raw_out = self.bc3_conn.checkSuccess(self.bc3_conn.sendCommand, find_file_cmd)
        stdout = raw_out['stdout'].strip()
        print('raw2 = ', raw_out)
        self.assertTrue(stdout == 'yes!')

        # remove the file so similar tests can be done
        rm_file_cmd = ['rm ' + destination + '/' + tfile]
        raw_out = self.bc3_conn.checkSuccess(self.bc3_conn.sendCommand, rm_file_cmd)
        if raw_out['return_code'] == 0:
            print('raw_out[\'return_code\'] = ', raw_out['return_code'])
            print('Warning! Remote file may not have been removed!')

if __name__ == '__main__':
        unittest.main()



################################################################################################################

# The Bc3 class has no methhods that can be tested without initiation and so we move straigh on to the remote testing

#class RemoteBc3ConnectionTest(unittest.TestCase):
#    """
#    This unit test is the first that should be performed. It will only check things that can be checked on the local computer. Tests that require a remote computer to connect to will be done in RemoteBaseConnectionTest.
#    """
#    # CLASS METHODS
#    @classmethod
#    def setUpClass(cls):
#        # create instance of the class
#        ssh_config_alias = input('Please enter the name in your .ssh/config file that you want to connect to (i.e. the host): ')
#        cls.ssh_config_alias = ssh_config_alias
#        cluster_user_name = input('Please enter the user name on the remote computer: ')
#        cls.cluster_user_name = cluster_user_name
#        bc3_conn = connections.Bc3(cluster_user_name, ssh_config_alias, 'test_forename', 'test_surname', 'test_email', '/test/output/path', '/test/runfiles/path', 'This is an imaginary cluster, created for' )
#        cls.bc3_conn = bc3_conn
#        # define  class variables needed throughout testing
#        cls.base_dir = 'base_connection_test_directory'
#        cls.sub_script_dir = 'base_connection_test_directory/submission_script_test'
#        cls.move_fname = 'base_connection_test_rsync_remote_transfer_file.txt'
#        cls.move_dir1 = 'base_connection_test_directory/test_createLocalFile/test_directory1'
#        cls.move_dir2 = 'base_connection_test_directory/test_createLocalFile/test_directory2'
#
#        # check that the base connection test directoy doesn't already exist
#        if os.path.isdir(cls.base_dir):
#            raise ValueError('The directory base_connection_test_directory must not exist, please move some where else.')
#
#        # create directories needed for test
#        pathlib.Path(cls.sub_script_dir).mkdir(parents=True, exist_ok=True)
#        pathlib.Path(cls.move_dir1).mkdir(parents=True, exist_ok=True)
#        pathlib.Path(cls.move_dir2).mkdir(parents=True, exist_ok=True)
#        # create a file for transfer tests
#        list_of_lines_of_file = ['This', 'is', 'a', 'test']
#        with open(cls.move_dir1 + "/" + cls.move_fname, mode = 'wt', encoding = 'utf-8') as myfile:
#            for line in list_of_lines_of_file:
#                myfile.write(line + "\n")
#
#    @classmethod
#    def tearDownClass(cls):
#        shutil.rmtree(cls.base_dir)
#
#    # TEST METHODS
#    def test_classCreation(self):
#        self.assertTrue(type(self.bc3_conn) == connections.Bc3)
#
#    def test_checkDiskUsage(self):
#        output_dict = self.bc3_conn.checkDiskUsage()
#        test_dict = {'usage': numbers.Number, 'soft_limit': numbers.Number, 'hard_limit': numbers.Number, 'units': str}
#        correct_keys = (set(output_dict.keys()) == set(test_dict.keys()))
#        correct_types = [isinstance(output_dict[key][1], test_dict[key]) for key in test_dict.keys()]
#        self.assertTrue((correct_keys and (sum(correct_types) == len(correct_types))))
#
#    def test_createWcmKoScript(self):
#        self.bc3_conn.createWcmKoScript('test_submission', self.sub_script_dir + '/test_submission_script.sh', '/test/wcm/master', '/test/output', '/test/outfiles', '/test/errorfiles', '/test/ko/codes.txt', '/test/ko/dir_names.txt', 100, 1)
#        my_file = Path(self.sub_script_dir + '/test_submission_script.sh')
#        raw_out = self.bc3_conn.localShellCommand(['wc', '-l', self.sub_script_dir + '/test_submission_script.sh'])[1].decode('utf-8')
#        no_lines = self.bc3_conn.getJobIdFromSubStdOut(raw_out)
#        self.assertTrue(my_file and (no_lines > 0))
#
#if __name__ == '__main__':
#        unittest.main()
