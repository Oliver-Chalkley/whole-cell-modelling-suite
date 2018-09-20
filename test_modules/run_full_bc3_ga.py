import sys
sys.path.insert(0, '/space/oc13378/myprojects/github/published_libraries/whole_cell_modelling_suite')
sys.path.insert(0, '/space/oc13378/myprojects/github/published_libraries/computer_communication_framework')
import whole_cell_modelling_suite.connections as connections
import whole_cell_modelling_suite.job_management as job_management
import whole_cell_modelling_suite.genetic_algorithms as genetic_algorithms
import pathlib
from statistics import mean

# CONNECTION DETAILS

# USER DETAILS STUFF
username = 'oc13378'
conn_alias = 'bc3'
forename = 'Oliver'
surname = 'Chalkley'
email = 'oc13378@bristol.ac.uk'
affiliation = 'Genome Design Group and Bristol Centre for Complexity Science'

# PATH STUFF
base_path_on_cluster = '/panfs/panasas01/bluegem-flex1/database/wcm_suite/tests'
output_path = 'output'
full_output_path = base_path_on_cluster + '/' + output_path
runfiles_path = 'runfiles'
full_runfiles_path = base_path_on_cluster + '/' + runfiles_path
wholecell_model_master = '/panfs/panasas01/bluegem-flex1/database/WholeCell-master'

bc3_conn = connections.Karr2012Bc3(username, conn_alias, forename, surname, email, full_output_path, full_runfiles_path, wholecell_model_master, affiliation = affiliation)

out_and_error_files = 'out_and_error_files'
full_out_and_error_files = base_path_on_cluster + '/' + out_and_error_files

createDataDictForSpecialistFunctionsFunctionName = 'createDataDictForKos'
createSubmissionScriptFunctionName = 'createWcmKoScript'
createDictOfFileSourceToFileDestinationsFunctionName = 'createDictOfFileSourceToFileDestinationForKos'
createAllFilesFunctionName = 'createAllFilesForKo'
getDataForDbFunctionName = 'getGrowthAndDivisionTime'

# INPUT PARAMETERS
standard_generation_no_to_pop_size_dict =  {-1: 15}

standard_random_kos_params_dict = {'populationSize_params_dict': standard_generation_no_to_pop_size_dict, 'getPopulationSizeFuncName': 'getPopulationSizeFromDict', 'getGeneCodeToIdDictFuncName': 'getGeneCodeToIdDictStandard', 'geneCodeToId_params_dict': None, 'min_ko_set_size': 2, 'max_ko_set_size': 5}

standardGetNewGeneration_params_dict = {'generationZeroFuncName': 'getRandomKos', 'genZero_params_dict': standard_random_kos_params_dict, 'noSurvivorsFuncName': 'getRandomKos', 'noSurvivors_params_dict': standard_random_kos_params_dict, 'minPopulationFuncName': 'getRandomKos', 'minPopulation_params_dict': standard_random_kos_params_dict, 'hasNoLengthFuncName': 'getRandomKos', 'noLength_params_dict': standard_random_kos_params_dict, 'min_population_to_start_mating': 4, 'mate_the_fittest_dict': {'getFittestProbabilitiesFuncName': 'getLinearProbsForMaximising', 'fittestProbabilities_params_dict': None, 'populationSize_params_dict': standard_generation_no_to_pop_size_dict, 'getPopulationSizeFuncName': 'getPopulationSizeFromDict', 'mateTwoParentsFuncName': 'mixMate', 'mateTwoParents_params_dict': None, 'mutateChildFuncName': 'exponentialMutation', 'mutateChild_params_dict': {'mutation_probability': 0.1, 'exponential_parameter': 2}}}

createJobSubmisions_params_dict = {'createAllFilesFuncName': createAllFilesFunctionName, 'createDataDictForSpecialistFunctionsFunctionName': createDataDictForSpecialistFunctionsFunctionName, 'createSubmissionScriptFunctionName': createSubmissionScriptFunctionName, 'createDictOfFileSourceToFileDestinationsFunctionName': createDictOfFileSourceToFileDestinationsFunctionName, 'first_wait_time': 3600, 'second_wait_time': 900}

# CREATE GA INSTANCE
ga_inst = genetic_algorithms.Karr2012GeneticAlgorithmGeneKo({'bc3': bc3_conn}, 'first_full_GA_KO_test', 'ga_test_output', 3, 'stopAtMaxGeneration', {'max_generation': 10}, 'standardGetNewGeneration', standardGetNewGeneration_params_dict, 'standardRunSimulations', {'createJobSubmissionFuncName': 'standardKoSubmissionFunction', 'createJobSubmisions_params_dict': createJobSubmisions_params_dict}, 20, genetic_algorithms.Karr2012MgaBase.getGeneCodesToIdDict(bc3_conn, genetic_algorithms.Karr2012MgaBase.getJr358Genes()), '/space/oc13378/myprojects/github/published_libraries/whole-cell-modelling-suite/whole-cell-modelling-suite/temp_storage', 'max', 'aliveAndSmallestGenome', {'overallScoreFuncName': 'overallScoreBasic', 'rawScoreFunc': mean})
ga_inst.run()
