import sys
sys.path.insert(0, '/space/oc13378/myprojects/github/published_libraries/whole_cell_modelling_suite')
from whole_cell_modelling_suite.genetic_algorithms import Karr2012GeneticAlgorithmGeneKo
import random
import numpy as np

class Karr2012RunFixedSetOfSims(Karr2012GeneticAlgorithmGeneKo):
    def __init__(self, child_name_to_genome_dict, dict_of_cluster_instances, MGA_name, MGA_description, cluster_queue_name, relative2clusterBasePath_simulation_output_path, repetitions_of_a_unique_simulation, submissionManagerFuncName, submissionManager_params_dict, runSimulationsFuncName, runSims_params_dict, all_gene_code_to_id_dict, temp_storage_path, updateFittestFuncName, extractAndScoreFuncName, extractAndScore_params_dict):
        Karr2012GeneticAlgorithmGeneKo.__init__(self, dict_of_cluster_instances, MGA_name, MGA_description, cluster_queue_name, relative2clusterBasePath_simulation_output_path, repetitions_of_a_unique_simulation, submissionManagerFuncName, submissionManager_params_dict, 'stopAtMaxGeneration', {'max_generation': 0}, 'returnFixedSetOfSims', None, runSimulationsFuncName, runSims_params_dict, 0, all_gene_code_to_id_dict, temp_storage_path, updateFittestFuncName, 'max', extractAndScoreFuncName, extractAndScore_params_dict)
        self.child_name_to_genome_dict = child_name_to_genome_dict.copy()

    def returnFixedSetOfSims(self, NewGen_params_dict):
        return self.child_name_to_genome_dict

class Gama(Karr2012GeneticAlgorithmGeneKo):
    def __init__(self, focus_ko_set, dict_of_cluster_instances, MGA_name, MGA_description, cluster_queue_name, relative2clusterBasePath_simulation_output_path, repetitions_of_a_unique_simulation, submissionManagerFuncName, submissionManager_params_dict, checkStopFuncName, checkStop_params_dict, getNewGenerationFuncName, newGen_params_dict, runSimulationsFuncName, runSims_params_dict, max_no_of_fit_individuals, all_gene_code_to_id_dict, temp_storage_path, updateFittestFuncName, max_or_min, extractAndScoreFuncName, extractAndScore_params_dict, getGenerationNameFuncName = 'getGenerationNameSimple', genName_params_dict = {'prefix': 'gen'}, convertDataFunctionName = ''):
        Karr2012GeneticAlgorithmGeneKo.__init__(self, dict_of_cluster_instances, MGA_name, MGA_description, cluster_queue_name, relative2clusterBasePath_simulation_output_path, repetitions_of_a_unique_simulation, submissionManagerFuncName, submissionManager_params_dict, checkStopFuncName, checkStop_params_dict, getNewGenerationFuncName, newGen_params_dict, runSimulationsFuncName, runSims_params_dict, max_no_of_fit_individuals, all_gene_code_to_id_dict, temp_storage_path, updateFittestFuncName, max_or_min, extractAndScoreFuncName, extractAndScore_params_dict)
        self.fittest_individuals_container = {'guess': None, 'add': None, 'mate': None} # this is used to manage the fittest_individuals variable because the notion of fittest change depending on what stage of gama you're in
        self.focus_ko_set = focus_ko_set

# GUESS (GENERATION ZERO)

    def guess(self, guess_params_dict):
        # get all neccessary parameters
        all_gene_codes_list = self.focus_ko_set.copy()
        partitioned_gene_codes_list = self.randomPartitionFocusGenes(all_gene_codes_list, guess_params_dict['partitionFuncName'], guess_params_dict['partition_params_dict'])
        min_ko_percent = guess_params_dict['min_ko_percent']
        max_ko_percent = guess_params_dict['max_ko_percent']
        no_of_children_per_partition = guess_params_dict['no_of_children_per_partition']
        partition_names = ['partition' + str(idx) for idx in range(1, len(partitioned_gene_codes_list) + 1)]
        self.fittest_individuals_container['guess'] = {partition_name: [] for partition_name in partition_names}

        # randomly create children
        ko_code_sets_dict_by_partition = {partition_names[partition_idx]: [tuple(random.sample(partitioned_gene_codes_list[partition_idx], random.randint( max(2, round(min_ko_percent * len(partitioned_gene_codes_list[partition_idx]))), round(max_ko_percent * len(partitioned_gene_codes_list[partition_idx])) ))) for child_idx in range(no_of_children_per_partition)] for partition_idx in range(len(partitioned_gene_codes_list))}
        child_name_to_ko_code_sets_dict_by_partition = { partition_name: {'child' + str(child_idx + 1): ko_code_sets_dict_by_partition[partition_name][child_idx] for child_idx in range(len(ko_code_sets_dict_by_partition[partition_name]))} for partition_name in ko_code_sets_dict_by_partition.keys()}
        child_name_to_genome_dict_by_partition = { partition_name: {child_name: self.convertCodesToGenomes(child_name_to_ko_code_sets_dict_by_partition[partition_name][child_name]) for child_name in child_name_to_ko_code_sets_dict_by_partition[partition_name].keys()} for partition_name in child_name_to_ko_code_sets_dict_by_partition.keys()}
        child_name_to_child_genome_dict = {partition_name + '_' + child_name: child_name_to_genome_dict_by_partition[partition_name][child_name] for partition_name in child_name_to_genome_dict_by_partition.keys() for child_name in child_name_to_genome_dict_by_partition[partition_name].keys()}

        return child_name_to_child_genome_dict

    def add(self, add_params_dict):
        viable_guesses_by_partition = self.fittest_individuals_container['guess'].copy()
        number_of_children = add_params_dict['number_of_children']
        min_number_of_partitions = add_params_dict['min_number_of_partitions']
        max_number_of_partitions = add_params_dict['max_number_of_partitions']
        child_names = ['add_child' + str(idx + 1) for idx in range(number_of_children)]
        child_name_to_ko_code_set = {}
        for child_idx in range(number_of_children):
            tmp_number_of_partitions = random.randint(min_number_of_partitions, max_number_of_partitions)
            list_of_partition_names_to_add = random.sample(list(viable_guesses_by_partition.keys()), tmp_number_of_partitions)
            new_ko_set = []
            for partition_name in list_of_partition_names_to_add:
                new_ko_set = list( set( new_ko_set ) + set( random.sample(viable_guesses_by_partition[partition_name], 1) ) )

            child_name_to_ko_code_set[child_names[child_idx]] = new_ko_set.copy()

        # convert codes to genomes
        child_name_to_child_genome_dict = {child_name: self.convertCodesToGenomes(child_name_to_ko_code_set[child_name] for child_name in child_name_to_ko_code_set.keys())}

        return child_name_to_child_genome_dict

    def gamaUpdateFittestPopulation(self, submission_instance, submission_management_instance, extractAndScoreContendersFuncName, extractContender_params_dict, max_or_min):
        if self.generation_counter == 0:
            output = guessUpdateFittestPopulation(submission_instance, submission_management_instance, extractAndScoreContendersFuncName, extractContender_params_dict, max_or_min)
        else:
            output = standardUpdateFittestPopulation(submission_instance, submission_management_instance, extractAndScoreContendersFuncName, extractContender_params_dict, max_or_min)

        return output

    def guessUpdateFittestPopulation(self, submission_instance, submission_management_instance, extractAndScoreContendersFuncName, extractContender_params_dict, max_or_min):
        # self.fittest_individuals_container = {'guess': None, 'add': None, 'mate': None} # this is used to manage the fittest_individuals variable because the notion of fittest change depending on what stage of gama you're in
        # extract the survivors and update self.fittest_individuals_container
        ko_name_to_code_set_dict = submission_instance.ko_name_to_set_dict.copy()
        code_to_id_dict = self.all_gene_code_to_id_dict
        id_name_to_set_dict = {name: tuple(code_to_id_dict[code] for code in ko_name_to_code_set_dict[name]) for name in ko_name_to_code_set_dict.keys()}
        id_set_to_name_dict = Karr2012MgaBase.invertDictionary(id_name_to_set_dict)
        # extract survivors
        simulation_data_dict = submission_management_instance.final_simulation_data_dict.copy()
        dividing_cells = {}
        for tuple_of_ids in simulation_data_dict.keys():
            if any([indiv_data[-1] != 0 for indiv_data in simulation_data_dict[tuple_of_ids]]):
                dividing_cells[tuple_of_ids] = simulation_data_dict[tuple_of_ids]

        # group divided cells into partitions that they came from
        for divided_id_set in dividing_cells.keys():
            divided_name = id_set_to_name_dict[divided_id_set]
            for partition_name in self.fittest_individuals_container['guess'].keys():
                fit_into_partition = False
                if divided_name[:len(partition_name)] == partition_name:
                    fit_into_partition = True
                    self.fittest_individuals_container['guess'][partition_name].append(divided_id_set)
                
            if not fit_into_partition:
                print('ko_name_to_code_set_dict = ', ko_name_to_code_set_dict)
                print('simulation_data_dict = ', simulation_data_dict)
                print('dividing_cells = ', dividing_cells)
                raise ValueError('Every child has to come from a partition! list(dividing_cells.keys()) = ', list(dividing_cells.keys()), ' and list(self.fittest_individuals_container[\'guess\'].keys()) = ', list(self.fittest_individuals_container['guess'].keys()))

        return

## PARTITION METHODS

    def randomPartitionFocusGenes(self, list_of_gene_codes_to_partition, partitionFuncName, partition_params_dict):
        # this method will pick the same sets of code for each partition every time but we need it randomised so we will randomly mix the list before passing it to the function 
        mixed_codes = random.sample(list_of_gene_codes_to_partition, len(list_of_gene_codes_to_partition))
        partitioned_gene_codes = list(getattr(self, partitionFuncName)(mixed_codes, partition_params_dict))

        return partitioned_gene_codes

    def uniformFocusSetSplit(self, focus_ko_set, splitFocusSet_params_dict):
        # numpy split odd/prime numbers well so I want to know the size of the groups and then create my own. The reason for this is that numpy will pick the same elements of each partition but I need the element of each partition to be random
        number_of_groups = splitFocusSet_params_dict['number_of_groups']
        split_codes_np = list(np.array_split(focus_ko_set, number_of_groups))

        return [list(npa) for npa in split_codes_np]

