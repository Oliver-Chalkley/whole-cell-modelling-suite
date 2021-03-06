import unittest
import sys
sys.path.insert(0, '/space/oc13378/myprojects/github/published_libraries/whole_cell_modelling_suite')
sys.path.insert(0, '/space/oc13378/myprojects/github/published_libraries/computer_communication_framework')
import whole_cell_modelling_suite.connections as connections
import whole_cell_modelling_suite.job_management as job_management
import computer_communication_framework.base_mga as base_mga
import pathlib
import shutil
import os
import random
import numpy as np

# MGA is an abstract class so cannot be created for testing so we will create the first child GeneticAlgorithmBase and then test both in this unittest. However, we will skill any meethods that require major integration (i.e. longer tests like run_simulations) and do them in a seperate file.

# A child class must create the required abstract class but it doesn't make sense to implement them in GeneticAlgorithmBase and so to bby pass this we create a new chlid that passes the abstract classes that aren't satified

class ChildGeneticAlgorithmBase(base_mga.GeneticAlgorithmBase):
    def __init__(self, dict_of_cluster_instances, MGA_name, relative2clusterBasePath_simulation_output_path, repetitions_of_a_unique_simulation, checkStopFuncName, checkStop_params_dict, getNewGenerationFuncName, NewGeneration_params_dict, runSimulationsFuncName, runSims_params_dict):
        base_mga.GeneticAlgorithmBase.__init__(self, dict_of_cluster_instances, MGA_name, relative2clusterBasePath_simulation_output_path, repetitions_of_a_unique_simulation, checkStopFuncName, checkStop_params_dict, getNewGenerationFuncName, NewGeneration_params_dict, runSimulationsFuncName, runSims_params_dict)

    def postSimulationFunction(self):
        pass

    def submitAndMonitorJobOnCluster(self):
        pass

class Karr2012BgMgaAndGAbaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print('Setup starting!')

        ### CREATE INSTANCE OF THE CLASS

        # connection stuff

        ssh_config_alias = input('Please enter the name in your .ssh/config file that you want to connect to BlueGem with (i.e. the host): ')
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
            location_of_state_mat_file = '/space/oc13378/myprojects/github/published_libraries/whole_cell_modelling_suite/whole_cell_modelling_suite/test_data/state-20.mat'

        cls.relative_base_that_gets_deleted = 'wcms'
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
        cls.temp_storage_path = '/space/oc13378/myprojects/github/published_libraries/whole-cell-modelling-suite/whole-cell-modelling-suite/temp_storage'
        cls.createDataDictForSpecialistFunctionsFunctionName = 'createDataDictForKos'
        cls.createSubmissionScriptFunctionName = 'createWcmKoScript'
        cls.createDictOfFileSourceToFileDestinationsFunctionName = 'createDictOfFileSourceToFileDestinationForKos'
        cls.createAllFilesFunctionName = 'createAllFilesForKo'
        cls.functionToGetReleventData = 'getGrowthAndDivisionTime'
        cls.queue_name = 'cpu'
        cls.queue_nameUT = 'cpu'

        # CREATE SUBIMSSION INSTANCES
        cls.bg_wcm_ko_sub = job_management.SubmissionKarr2012(cls.submission_name, cls.bg_conn, cls.ko_name_to_set_dict, cls.queue_name, cls.full_output_path, cls.full_runfiles_path, cls.full_out_and_error_files, cls.full_out_and_error_files, cls.master_dir, cls.repetitions_of_a_unique_simulation, cls.createAllFilesFunctionName, cls.createDataDictForSpecialistFunctionsFunctionName, cls.createSubmissionScriptFunctionName, cls.createDictOfFileSourceToFileDestinationsFunctionName, first_wait_time = 1, second_wait_time = 1, temp_storage_path = cls.temp_storage_path)

        # CREATE A UNITTEST SUBMISION INSTANCE
        cls.master_dir = '/projects/flex1/database/wcm_suite/unittest/unittest-master'
        cls.createDataDictForSpecialistFunctionsFunctionNameUT = 'createDataDictForUnittest'
        cls.createSubmissionScriptFunctionNameUT = 'createUnittestScript'
        cls.createDictOfFileSourceToFileDestinationsFunctionNameUT = 'createDictOfFileSourceToFileDestinationForUnittest'
        cls.createAllFilesFunctionNameUT = 'createAllFilesForUnittest'
        cls.getDataForDbFunctionName = 'getGrowthAndDivisionTime'
        quick_list_of_states_to_convert = ['basic_summary']
        long_list_of_states_to_convert = ['basic_summary', 'mature_rna_counts', 'metabolic_reaction_fluxs', 'mature_protein_monomer_counts', 'mature_protein_complex_counts']
        list_of_states_to_convert = quick_list_of_states_to_convert.copy()
        cls.bg_unittest_ko_sub = job_management.SubmissionKarr2012(cls.submission_name, cls.bg_conn, cls.ko_name_to_set_dict, cls.queue_nameUT, cls.full_output_path, cls.full_runfiles_path, cls.full_out_and_error_files, cls.full_out_and_error_files, cls.master_dir, cls.repetitions_of_a_unique_simulation, cls.createAllFilesFunctionNameUT, cls.createDataDictForSpecialistFunctionsFunctionNameUT, cls.createSubmissionScriptFunctionNameUT, cls.createDictOfFileSourceToFileDestinationsFunctionNameUT, first_wait_time = 1, second_wait_time = 1, temp_storage_path = cls.temp_storage_path)

        # CREATE A JOB MANAGEMENT INSTANCE IN TEST MODE
        #cls.test_manager = job_management.SubmissionManagerKarr2012(cls.bg_unittest_ko_sub, cls.convertDataFunctionName, cls.updateCentralDbFunctionName, cls.getDataForDbFunctionName, list_of_states_to_save = list_of_states_to_convert, ko_db_path_relative_to_db_connection_flex1 = 'database/ko_db/unittest_ko_db/unittest_ko.db', test_mode = True)

        # CREATE A GENETIC ALGORITHM BASE INSTANCE

        cls.ga_base_inst = ChildGeneticAlgorithmBase({'bg': cls.bg_conn}, 'base_mga_unittest', 'unittest_sim_output', 1, 'stopAtMaxGeneration', {'max_generation': 5}, 'standardGetNewGeneration', {'generationZeroFuncName': 'getRandomKos', 'genZero_params_dict': None, 'noSurvivorsFuncName': 'getRandomKos', 'noSurvivors_params_dict': None, 'minPopulationFuncName': 'getRandomKos', 'minPopulation_params_dict': None, 'hasNoLengthFuncName': 'getRandomKos', 'noLength_params_dict': None, 'min_population_to_start_mating': 2, 'mate_the_fittest_dict': {'getFittestProbabilitiesFuncName': 'getLinearProbsForMaximising', 'fittestProbabilities_params_dict': None, 'populationSize_params_dict': {0: 200, -1: 100}, 'getPopulationSizeFuncName': 'getPopulationSizeFromDict', 'mateTwoParentsFuncName': 'mixMate', 'mateTwoParents_params_dict': None, 'mutateChildFuncName': 'exponentialMutation', 'mutateChild_params_dict': {'mutation_probability': 0.4, 'exponential_parameter': 2}}}, 'standardRunSimulationsUT', None)

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
        # delete temp local directories
        shutil.rmtree(cls.base_dir)
        shutil.rmtree(cls.temp_storage_path)

        # delete temp remote directories
        rm_remote_dirs_cmd = ['rm -r ' + cls.base_path_on_cluster + '/' + cls.relative_base_that_gets_deleted]
        raw_out = cls.bg_conn.checkSuccess(cls.bg_conn.sendCommand, rm_remote_dirs_cmd)
        # print warning if there was a problem with the remote connection
        if raw_out['return_code'] != 0:
            print('Warning, we could not delete the remote files, please do it manually as it may effect future tests. raw_out = ', raw_out)

    ### TEST METHODS

    def test_createGeneticAlgorithmBase(self):
        print('test_createGeneticAlgorithmBase')
        self.assertTrue( (type(self.ga_base_inst) is ChildGeneticAlgorithmBase) )

    def test_run(self):
        self.ga_base_inst.generation_counter = 0
        self.ga_base_inst.run()

        correct_max_gen_counter = 5

        self.assertTrue(self.ga_base_inst.generation_counter == correct_max_gen_counter)

    def test_stopAtMaxGeneration(self):
        max_gen = 5
        # perform max_tests random tests
        max_tests = 50
        test_results = [None] * max_tests
        for test_idx in range(max_tests):
            # create random generation
            self.ga_base_inst.generation_counter = random.randint(0, 10)
            tmp_result = self.ga_base_inst.stopAtMaxGeneration({'max_generation': max_gen})
            if self.ga_base_inst.generation_counter <= max_gen:
                test_results[test_idx] = not tmp_result
            else:
                test_results[test_idx] = tmp_result

        self.assertTrue(sum(test_results) == max_tests)

    def test_getPopulationSizeFromDict(self):
        gen_num_to_gen_size_dict = {0: 200, 1: 500, 7: 700, 21: 1000, -1: 100}
        # perform max_tests random tests
        max_tests = 50
        test_results = [None] * max_tests
        for test_idx in range(max_tests):
            # create random generation
            self.ga_base_inst.generation_counter = random.randint(0, 25)
            tmp_result = self.ga_base_inst.getPopulationSizeFromDict(gen_num_to_gen_size_dict)
            if self.ga_base_inst.generation_counter in gen_num_to_gen_size_dict:
                test_results[test_idx] = tmp_result == gen_num_to_gen_size_dict[self.ga_base_inst.generation_counter]
            else:
                test_results[test_idx] = tmp_result == gen_num_to_gen_size_dict[-1]

        self.assertTrue(sum(test_results) == max_tests)

    def test_getGenerationNameSimple(self):
        print('In test_getGenerationNameSimple!')
        # set generation counter to a known quantity to test
        self.ga_base_inst.generation_counter = 13
        none_test = self.ga_base_inst.getGenerationNameSimple({'prefix': None})
        test_test = self.ga_base_inst.getGenerationNameSimple({'prefix': 'test'})

        self.assertTrue(none_test == 'gen13' and test_test == 'test13')

    def test_spreadChildrenAcrossClusters(self):
        print('In test_spreadChildrenAcrossClusters!')

        # we will spread 10 children kos across 2 clusters
        no_of_children = 10
        no_of_clusters = 2

        # only BG cluster so add a fake bc3
        self.ga_base_inst.cluster_instances_dict['bc3'] = None

        # create fake simulations
        child_name_to_genome_dict = {'ko' + str(no): None for no in range(1, no_of_children + 1)}

        # run method
        child_name_to_genome_dict_by_cluster = self.ga_base_inst.spreadChildrenAcrossClusters(child_name_to_genome_dict)

        correct_no_of_children_per_cluster = no_of_children / no_of_clusters

        self.assertTrue( (len(child_name_to_genome_dict_by_cluster) == no_of_clusters ) and ( len(list(child_name_to_genome_dict_by_cluster.values())[0]) == correct_no_of_children_per_cluster ) )

    def test_spreadChildrenAcrossJobs(self):
        print('In test_spreadChildrenAcrossJobs!')

        # we will spread 10 children kos across 2 clusters
        no_of_children = 2000
        no_of_clusters = 2
        max_children_per_job = 200

        # only BG cluster so add a fake bc3
        self.ga_base_inst.cluster_instances_dict['bc3'] = None

        # create fake simulations
        child_name_to_genome_dict = {'ko' + str(no): None for no in range(1, no_of_children + 1)}

        # run method
        child_name_to_genome_dict_by_cluster = self.ga_base_inst.spreadChildrenAcrossClusters(child_name_to_genome_dict)
        child_name_to_genome_dict_by_jobs_by_cluster = self.ga_base_inst.spreadChildrenAcrossJobs(child_name_to_genome_dict_by_cluster, max_children_per_job)

        correct_no_of_children_per_cluster = no_of_children / no_of_clusters
        correct_no_of_jobs_per_cluster = correct_no_of_children_per_cluster / max_children_per_job

        self.assertTrue( (len(child_name_to_genome_dict_by_jobs_by_cluster) == no_of_clusters ) and ( len(list(child_name_to_genome_dict_by_jobs_by_cluster.values())[0]) == correct_no_of_jobs_per_cluster ) and ( len(list(child_name_to_genome_dict_by_jobs_by_cluster.values())[0][0]) == max_children_per_job ) )

# Testing GeneticAlgorithmBase now. Will start with the simple functions first like mixMate etc and then move onto the more complicated ones that integrate many methods

    def test_sliceMate(self):
        # This test basically just tries a load of random parents of different sizes and checks that it returns a child of the correct size
        print('In sliceMate!')

        # create a lots of tests in a loop
        no_of_tests = 1000
        test_list = [0 for idx in range(no_of_tests)]
        for idx in range(no_of_tests):
            random_length = random.randint(2, int(no_of_tests / 2))
            # create two random parents
            two_parents = np.random.randint(2, size=[random_length, 2])

            # function can take either lists or tuples so randomly send both
            if random.random() < 0.5:
                child = self.ga_base_inst.sliceMate(list(two_parents[:, 0]), list(two_parents[:,1]), None)
            else:
                child = self.ga_base_inst.sliceMate(tuple(two_parents[:, 0]), tuple(two_parents[:,1]), None)

            test_list[idx] = len(child) == random_length

        self.assertTrue(sum(test_list) == len(test_list))

    def test_mixMate(self):
        # This test basically just tries a load of random parents of different sizes and checks that it returns a child of the correct size
        print('In mixMate!')

        # create a lots of tests in a loop
        no_of_tests = 1000
        test_list = [0 for idx in range(no_of_tests)]
        for idx in range(no_of_tests):
            # create two random parents
            random_length = random.randint(2, int(no_of_tests / 2))
            two_parents = np.random.randint(2, size=[random_length, 2])

            # function can take either lists or tuples so randomly send both
            if random.random() < 0.5:
                child = self.ga_base_inst.mixMate(list(two_parents[:, 0]), list(two_parents[:,1]), None)
            else:
                child = self.ga_base_inst.mixMate(tuple(two_parents[:, 0]), tuple(two_parents[:,1]), None)

            test_list[idx] = len(child) == random_length

        self.assertTrue(sum(test_list) == len(test_list))

    def test_uniformMutation(self):
        print('In uniformMutation!')

        no_of_tests = 1000
        test_list = [0 for idx in range(no_of_tests)]
        for idx in range(no_of_tests):
            # create a WT child (then we know what's been muatated)
            random_length = random.randint(2, no_of_tests)
            child = [1] * random_length
            # randomly pick number of mutations
            no_mutations = random.randint(1, random_length)

            child = self.ga_base_inst.uniformMutation(list(child), {'mutation_probability': 1, 'number_of_mutations': no_mutations})

            test_list[idx] = ( (len(child) == random_length) and (sum(child) == (random_length - no_mutations)) )

        self.assertTrue(len(test_list) == sum(test_list))

    def test_exponentialMutation(self):
        print('In exponentialMutation!')

        no_of_tests = 1000
        test_list = [0 for idx in range(no_of_tests)]
        list_of_mutation_counts = [0 for idx in range(no_of_tests)]
        for idx in range(no_of_tests):
            # create a WT child (then we know what's been muatated)
            random_length = random.randint(4, no_of_tests)
            child = [1] * random_length
            # create random exponential parameter
            expo_param = random.randint(2, int(random_length / 2))

            child = self.ga_base_inst.exponentialMutation(list(child), {'mutation_probability': 1, 'exponential_parameter': expo_param})

            # don't think it's worth checking the distribution is actually exponetial so will do a rougher test
            list_of_mutation_counts[idx] = child.count(0)
            test_list[idx] = ( (len(child) == random_length) and (sum(child) != random_length) )

        self.assertTrue( (len(test_list) == sum(test_list)) and (len(set(list_of_mutation_counts)) > 2) ) # technically this could  be one but I thought making it > 2 gives it a slightly bigger margin of error

    def test_getLinearProbsForMaximising(self):
        print('In getLinearProbsForMaximising!')

        # set constants
        genome_length = 500
        no_of_fittest = 50

        # create fake fittest individuals
        genomes = np.random.randint(2, size=[genome_length, no_of_fittest])
        genome_features_and_scores = [[random.randint(1, 100), random.randint(1, 100)] for idx in range(no_of_fittest)]
        self.ga_base_inst.fittest_individuals = {tuple(genomes[idx]): genome_features_and_scores[idx] for idx in range(no_of_fittest)}

        probabilities = self.ga_base_inst.getLinearProbsForMaximising(None)

        self.assertTrue( (len(probabilities) == no_of_fittest) and (round(sum(probabilities)) == 1) )

    def test_mateTheFittest(self):
        # set constants
        genome_length = 500
        no_of_fittest = 50

        # create fake fittest individuals
        genomes = np.random.randint(2, size=[genome_length, no_of_fittest])
        genome_features_and_scores = [[random.randint(1, 100), random.randint(1, 100)] for idx in range(no_of_fittest)]
        self.ga_base_inst.fittest_individuals = {tuple(genomes[idx]): genome_features_and_scores[idx] for idx in range(no_of_fittest)}

        # create params_dict
        mate_fittest_params_dict = {'getFittestProbabilitiesFuncName': 'getLinearProbsForMaximising', 'fittestProbabilities_params_dict': None, 'populationSize_params_dict': {0: 500, 1: 200, -1: 100}, 'getPopulationSizeFuncName': 'getPopulationSizeFromDict', 'mateTwoParentsFuncName': 'mixMate', 'mateTwoParents_params_dict': None, 'mutateChildFuncName': 'exponentialMutation', 'mutateChild_params_dict': {'mutation_probability': 0.4, 'exponential_parameter': 2}}
        dict_checks = [0] * 3
        pop_size_dict = {0: 500, 1: 200, 2: 100}
        pop_size_checks = [0] * 3
        for gen_no in range(3):
            self.ga_base_inst.generation_counter = gen_no
            child_name_to_genome_dict = self.ga_base_inst.mateTheFittest(mate_fittest_params_dict)
            dict_checks[gen_no] = type(child_name_to_genome_dict) is dict
            pop_size_checks[gen_no] = len(child_name_to_genome_dict) == pop_size_dict[gen_no]

        self.assertTrue( ( sum(dict_checks) == len(dict_checks) ) and (  sum(pop_size_checks) == len(pop_size_checks) ) )

if __name__ == '__main__':
        unittest.main()

