import sys
import random
sys.path.insert(0, '/home/oli/git/published_libraries/computer_communication_framework')
sys.path.insert(0, '/home/oli/git/published_libraries/whole_cell_modelling_suite')
from computer_communication_framework.base_mga import GeneticAlgorithmBase
#import whole_cell_modelling_suite.job_management as job_management
from whole_cell_modelling_suite.job_management import SubmissionKarr2012, SubmissionManagerKarr2012
from concurrent.futures import ProcessPoolExecutor as Pool

class Karr2012MgaBase():
    """
    This only a suite a methods that MGAs might use when operating on the Karr et al. 2012 whole-cell model.
    """
    
    def __init__(self):
        pass
        
    # All the following methods are static because they are common tools and it is useful to be able to access them wihtout creating an instance.

    # STATIC METHODS

    def convert_genome_to_codes(self, genome):
        id_to_code_dict = self.id_to_code_dict.copy()
        idx_to_id_dict = self.genome_idx_to_id_dict.copy()

        return tuple([id_to_code_dict[idx_to_id_dict[idx]] for idx in range(len(genome)) if genome[idx] == 0])

    @staticmethod
    def random_combination(iterable_of_all_posible_indexs, length_of_combination):
            "Random selection from itertools.combinations(iterable_of_all_posible_indexs, length_of_combination)"
            pool = tuple(iterable_of_all_posible_indexs)
            n = len(pool)
            indices = sorted(random.sample(range(n), length_of_combination))

            return tuple(pool[i] for i in indices)

    @staticmethod
    def random_pick(list_of_options, probabilities):
        x = random.uniform(0, 1)
        cumulative_probability = 0.0
        for idx in range(len(list_of_options)):
            cumulative_probability += probabilities[idx]
            if x < cumulative_probability: 
                break

        return list_of_options[idx]

    @staticmethod
    def getGeneCodesToIdDict(conn, tuple_of_gene_codes):
        """Creates a dictionary who's keys are the gene codes from tuple_of_gene_codes and values are the gene ID acording to our database."""
        gene_code_to_id_dict = conn.db_connection.convertGeneCodeToId(tuple_of_gene_codes)

        return gene_code_to_id_dict

    @staticmethod
    def invertDictionary(input_dict):
        """This function takes a dictionary and inverts it (assuming it's one to one)."""
        inverse_dict = {v: k for k, v in input_dict.items()}

        return inverse_dict

    @staticmethod
    def createIdxToIdDict(code_to_id_dict):
        list_of_ids = list(code_to_id_dict.values())
        # sort them into ascending order (just because the order of dicts aren't alwayys preserved and so provided we are using the genes to start with we can compare the indexs provided they are ordered in ascending order) maybe not neccessary but avoiding hard to find bug later on
        list_of_ids.sort()
        idx_to_id_dict = {idx: list_of_ids[idx] for idx in range(len(list_of_ids))}

        return idx_to_id_dict

    @staticmethod
    def convertIdxToGeneId(gene_indexs_list, index_to_id_dict):
        """
        """
        # test input is of the right form
        if not (type(gene_indexs_list) is list and type(index_to_id_dict) is dict):
            raise TypeError('gene_indexs_list must be a list (even if only one value!) and index_to_id_dict must be a dictionary. Here type(gene_indexs_list)=', type(gene_indexs_list), ' and type(index_to_id_dict)=', type(index_to_id_dict))

        gene_id_list = [index_to_id_dict[idx] for idx in gene_indexs_list]

        return gene_id_list

    @staticmethod
    def convertGeneIdToCode(gene_id_list):
        """
        """
        # test input is of the right form
        if not (type(gene_id_list) is list):
            raise TypeError('gene_id_list must be a list (even if only one value!). Here type(gene_indexs_list)=', type(gene_indexs_list))

        gene_id_list = [index_to_id_dict[idx] for idx in gene_id_list]

    @staticmethod
    def getJr358Genes():
        """The function returns the 358 genes that Joshua Rees classified for potential KOs."""
        return ('MG_001', 'MG_003', 'MG_004', 'MG_005', 'MG_006', 'MG_007', 'MG_008', 'MG_009', 'MG_012', 'MG_013', 'MG_014', 'MG_015', 'MG_019', 'MG_020', 'MG_021', 'MG_022', 'MG_023', 'MG_026', 'MG_027', 'MG_029', 'MG_030', 'MG_031', 'MG_033', 'MG_034', 'MG_035', 'MG_036', 'MG_037', 'MG_038', 'MG_039', 'MG_040', 'MG_041', 'MG_042', 'MG_043', 'MG_044', 'MG_045', 'MG_046', 'MG_047', 'MG_048', 'MG_049', 'MG_050', 'MG_051', 'MG_052', 'MG_053', 'MG_055', 'MG_473', 'MG_058', 'MG_059', 'MG_061', 'MG_062', 'MG_063', 'MG_064', 'MG_065', 'MG_066', 'MG_069', 'MG_070', 'MG_071', 'MG_072', 'MG_073', 'MG_075', 'MG_077', 'MG_078', 'MG_079', 'MG_080', 'MG_081', 'MG_082', 'MG_083', 'MG_084', 'MG_085', 'MG_086', 'MG_087', 'MG_088', 'MG_089', 'MG_090', 'MG_091', 'MG_092', 'MG_093', 'MG_094', 'MG_097', 'MG_098', 'MG_099', 'MG_100', 'MG_101', 'MG_102', 'MG_476', 'MG_104', 'MG_105', 'MG_106', 'MG_107', 'MG_109', 'MG_110', 'MG_111', 'MG_112', 'MG_113', 'MG_114', 'MG_118', 'MG_119', 'MG_120', 'MG_121', 'MG_122', 'MG_123', 'MG_124', 'MG_126', 'MG_127', 'MG_128', 'MG_130', 'MG_132', 'MG_136', 'MG_137', 'MG_139', 'MG_141', 'MG_142', 'MG_143', 'MG_145', 'MG_149', 'MG_150', 'MG_151', 'MG_152', 'MG_153', 'MG_154', 'MG_155', 'MG_156', 'MG_157', 'MG_158', 'MG_159', 'MG_160', 'MG_161', 'MG_162', 'MG_163', 'MG_164', 'MG_165', 'MG_166', 'MG_167', 'MG_168', 'MG_169', 'MG_170', 'MG_171', 'MG_172', 'MG_173', 'MG_174', 'MG_175', 'MG_176', 'MG_177', 'MG_178', 'MG_179', 'MG_180', 'MG_181', 'MG_182', 'MG_183', 'MG_184', 'MG_186', 'MG_187', 'MG_188', 'MG_189', 'MG_190', 'MG_191', 'MG_192', 'MG_194', 'MG_195', 'MG_196', 'MG_197', 'MG_198', 'MG_200', 'MG_201', 'MG_203', 'MG_204', 'MG_205', 'MG_206', 'MG_208', 'MG_209', 'MG_210', 'MG_481', 'MG_482', 'MG_212', 'MG_213', 'MG_214', 'MG_215', 'MG_216', 'MG_217', 'MG_218', 'MG_221', 'MG_224', 'MG_225', 'MG_226', 'MG_227', 'MG_228', 'MG_229', 'MG_230', 'MG_231', 'MG_232', 'MG_234', 'MG_235', 'MG_236', 'MG_238', 'MG_239', 'MG_240', 'MG_244', 'MG_245', 'MG_249', 'MG_250', 'MG_251', 'MG_252', 'MG_253', 'MG_254', 'MG_257', 'MG_258', 'MG_259', 'MG_261', 'MG_262', 'MG_498', 'MG_264', 'MG_265', 'MG_266', 'MG_270', 'MG_271', 'MG_272', 'MG_273', 'MG_274', 'MG_275', 'MG_276', 'MG_277', 'MG_278', 'MG_282', 'MG_283', 'MG_287', 'MG_288', 'MG_289', 'MG_290', 'MG_291', 'MG_292', 'MG_293', 'MG_295', 'MG_297', 'MG_298', 'MG_299', 'MG_300', 'MG_301', 'MG_302', 'MG_303', 'MG_304', 'MG_305', 'MG_309', 'MG_310', 'MG_311', 'MG_312', 'MG_315', 'MG_316', 'MG_317', 'MG_318', 'MG_321', 'MG_322', 'MG_323', 'MG_324', 'MG_325', 'MG_327', 'MG_329', 'MG_330', 'MG_333', 'MG_334', 'MG_335', 'MG_517', 'MG_336', 'MG_339', 'MG_340', 'MG_341', 'MG_342', 'MG_344', 'MG_345', 'MG_346', 'MG_347', 'MG_349', 'MG_351', 'MG_352', 'MG_353', 'MG_355', 'MG_356', 'MG_357', 'MG_358', 'MG_359', 'MG_361', 'MG_362', 'MG_363', 'MG_522', 'MG_365', 'MG_367', 'MG_368', 'MG_369', 'MG_370', 'MG_372', 'MG_375', 'MG_376', 'MG_378', 'MG_379', 'MG_380', 'MG_382', 'MG_383', 'MG_384', 'MG_385', 'MG_386', 'MG_387', 'MG_390', 'MG_391', 'MG_392', 'MG_393', 'MG_394', 'MG_396', 'MG_398', 'MG_399', 'MG_400', 'MG_401', 'MG_402', 'MG_403', 'MG_404', 'MG_405', 'MG_407', 'MG_408', 'MG_409', 'MG_410', 'MG_411', 'MG_412', 'MG_417', 'MG_418', 'MG_419', 'MG_421', 'MG_424', 'MG_425', 'MG_426', 'MG_427', 'MG_428', 'MG_429', 'MG_430', 'MG_431', 'MG_433', 'MG_434', 'MG_435', 'MG_437', 'MG_438', 'MG_442', 'MG_444', 'MG_445', 'MG_446', 'MG_447', 'MG_448', 'MG_451', 'MG_453', 'MG_454', 'MG_455', 'MG_457', 'MG_458', 'MG_460', 'MG_462', 'MG_463', 'MG_464', 'MG_465', 'MG_466', 'MG_467', 'MG_468', 'MG_526', 'MG_470')

class Karr2012GeneticAlgorithmGeneKo(GeneticAlgorithmBase, Karr2012MgaBase):
    """
    """
    def __init__(self, dict_of_cluster_instances, MGA_name, relative2clusterBasePath_simulation_output_path, repetitions_of_a_unique_simulation, checkStopFuncName, checkStop_params_dict, getNewGenerationFuncName, newGen_params_dict, runSimulationsFuncName, runSims_params_dict, max_no_of_fit_individuals, all_gene_code_to_id_dict, temp_storage_path, max_or_min, extractAndScoreFuncName, extractAndScore_params_dict, getGenerationNameFuncName = 'getGenerationNameSimple', genName_params_dict = {'prefix': 'gen'}, convertDataFunctionName = ''):
        GeneticAlgorithmBase.__init__(self, dict_of_cluster_instances, MGA_name, relative2clusterBasePath_simulation_output_path, repetitions_of_a_unique_simulation, checkStopFuncName, checkStop_params_dict, getNewGenerationFuncName, newGen_params_dict, runSimulationsFuncName, runSims_params_dict, max_no_of_fit_individuals, temp_storage_path)
        Karr2012MgaBase.__init__(self)
        self.extractAndScoreFuncName = extractAndScoreFuncName
        self.extractAndScore_params_dict = extractAndScore_params_dict
        self.max_or_min = max_or_min
        self.getGenerationNameFuncName = getGenerationNameFuncName
        self.genName_params_dict = genName_params_dict
        self.all_gene_code_to_id_dict = all_gene_code_to_id_dict # WARNING: THERE WILL BE FUNCATIONALITY TO WORK WITH DIFFERENT GENOMES DEPENDING ON WHERE IN THE ALGORITHM YOU ARE SO THE "ALL" HERE MEANS IT IS THE LARGEEST POSSIBLE SET TO FALL BACK ON. THIS MIGHT MEAN THAT RANDOM KOS FUNCTION MIGHT BE WORKING OFF A DIFFERENT SET OF GENES FOR EXAMPLE
        self.id_to_code_dict = Karr2012MgaBase.invertDictionary(self.all_gene_code_to_id_dict)
        self.order_of_ids_in_genome = sorted(list(self.all_gene_code_to_id_dict.values()))
        self.genome_idx_to_id_dict = {idx: self.order_of_ids_in_genome[idx] for idx in range(len(self.order_of_ids_in_genome))}

    ### METHODS RELATED TO CREATING JOB SUBMISSION INSTANCES

    def standardKoSubmissionFunction(self, in_dict):
        # the genetic algorithm classes work with the genome representation of simulations but the model works with KO set representations so the first thing we need to do is convert from genome to KO represnetations
        required_keys = ('cluster_conn', 'single_child_name_to_genome_dict', 'createAllFilesFuncName', 'createDataDictForSpecialistFunctionsFunctionName', 'createSubmissionScriptFunctionName', 'createDictOfFileSourceToFileDestinationsFunctionName')

        if not ( sum([key in in_dict for key in required_keys]) == len(required_keys) ):
            raise ValueError('in_dict must contain the keys: ', required_keys, '. Here list(in_dict.keys()) = ', list(in_dict.keys()))

        cluster_conn = in_dict['cluster_conn']
        single_child_name_to_genome_dict = in_dict['single_child_name_to_genome_dict'].copy()
        queue_name = cluster_conn.ko_queue
        submission_name = self.MGA_name + '_' + self.getGenerationName(self.getGenerationNameFuncName, self.genName_params_dict)
        cluster_connection = cluster_conn
        ko_name_to_set_dict = {name: self.convert_genome_to_codes(single_child_name_to_genome_dict[name]) for name in single_child_name_to_genome_dict.keys()}
        simulation_output_path = cluster_connection.base_output_path + '/' + self.relative2clusterBasePath_simulation_output_path + '/' + self.MGA_name + '/' + self.getGenerationName(self.getGenerationNameFuncName, self.genName_params_dict)
        errorfile_path = cluster_connection.base_output_path + '/' + self.relative2clusterBasePath_simulation_output_path + '/' + self.MGA_name + '/' + self.getGenerationName(self.getGenerationNameFuncName, self.genName_params_dict)
        outfile_path = cluster_connection.base_output_path + '/' + self.relative2clusterBasePath_simulation_output_path + '/' + self.MGA_name + '/' + self.getGenerationName(self.getGenerationNameFuncName, self.genName_params_dict)
        runfiles_path = cluster_connection.base_runfiles_path + '/' + self.relative2clusterBasePath_simulation_output_path + '/' + self.MGA_name + '/' + self.getGenerationName(self.getGenerationNameFuncName, self.genName_params_dict)

        job_submission_inst = SubmissionKarr2012(submission_name, cluster_connection, ko_name_to_set_dict, queue_name, simulation_output_path, runfiles_path, errorfile_path, outfile_path, cluster_connection.wholecell_master_dir, self.reps_of_unique_sim, in_dict['createAllFilesFuncName'], in_dict['createDataDictForSpecialistFunctionsFunctionName'], in_dict['createSubmissionScriptFunctionName'], in_dict['createDictOfFileSourceToFileDestinationsFunctionName'], first_wait_time = in_dict['first_wait_time'], second_wait_time = in_dict['second_wait_time'], temp_storage_path = self.temp_storage_path)

        return job_submission_inst

    ### ABSTRACT METHOD SATISIFICATION

    def submitAndMonitorJobsOnCluster(self, dict_of_submission_instances):
        list_of_cluster_instance_keys = list(dict_of_submission_instances.keys())
        with Pool() as pool:
            list_of_management_instances = list(pool.map(SubmissionManagerKarr2012, zip([dict_of_submission_instances[clust_inst_key] for clust_inst_key in dict_of_submission_instances], [self.all_gene_code_to_id_dict] * len(dict_of_submission_instances), [self.id_to_code_dict] * len(dict_of_submission_instances), ['convertMatToPandas'] * len(dict_of_submission_instances), ['updateDbGenomeReduction2017'] * len(dict_of_submission_instances), ['getGrowthAndDivisionTime'] * len(dict_of_submission_instances), ['database/ko_db/unittest_ko_db/unittest_ko.db'] * len(dict_of_submission_instances), [self.genome_idx_to_id_dict] * len(dict_of_submission_instances), [['basic_summary']] * len(dict_of_submission_instances), ['database/ko_db/library'] * len(dict_of_submission_instances), ['database/staticDB/static.db'] * len(dict_of_submission_instances), [False] * len(dict_of_submission_instances))))

        # convert list into the dict that the rest of the library is expecting
        management_inst = {list_of_cluster_instance_keys[idx]: list_of_management_instances[idx] for idx in range(len(list_of_management_instances))}
        # update the fittest population
        for cluster_connection in list_of_cluster_instance_keys:
            self.updateFittestPopulation(dict_of_submission_instances[cluster_connection], management_inst[cluster_connection], self.extractAndScoreFuncName, self.extractAndScore_params_dict, self.max_or_min)

        return list_of_management_instances

    def postSimulationFunction(self, submission_instances, management_instances):
        pass

    ### METHODS REALTED TO GETTING GENE CODE TO ID DICT
    def getGeneCodeToIdDictStandard(self, tuple_of_codes):
        if tuple_of_codes is None:
            gene_code_to_id_dict = self.all_gene_code_to_id_dict.copy()
        else:
            all_gene_code_to_id_dict = self.all_gene_code_to_id_dict.copy()
            gene_code_to_id_dict = {code: all_gene_code_to_id_dict[code] for code in tuple_of_codes}

        return gene_code_to_id_dict

    ### FUNCTIONS TO GENERATE SETS OF CHILDREN
    ### IMPORTANT THE WCM WORKS IN GENE KOS BUT THE WCM SUITE WORKS IN GENOMES SO ANY METHOD THAT GETS A GENERATION NEEDS TO OUTPUT IN GENOMES AND ANY METHOD THAT SUBMITS JOBS TO A CLUSTER MUST CONVERT GENOMES INTO KO SETS

    def getRandomKos(self, newGen_params_dict):
        submission_name = self.getGenerationName(self.getGenerationNameFuncName, self.genName_params_dict)
        population_size = self.getPopulationSize(newGen_params_dict['getPopulationSizeFuncName'], newGen_params_dict['populationSize_params_dict'])
        # get gene code to gene ID dictionary for every possible gene that we want to pick from
        gene_code_to_id_dict = getattr(self, newGen_params_dict['getGeneCodeToIdDictFuncName'])(newGen_params_dict['geneCodeToId_params_dict'])
        # In the "genome form" we need to map the index of the genome to a gene ID.
        idx_to_ids_dict = self.genome_idx_to_id_dict.copy()
        id_to_idx_dict = self.invertDictionary(idx_to_ids_dict)
        list_of_ids = list(gene_code_to_id_dict.values())
        list_of_ids.sort()
        all_possible_idxs_iter = range(len(list_of_ids))
        # create the inverse dictionary
        gene_id_to_code_dict = self.invertDictionary(gene_code_to_id_dict)
        ko_name_to_set_dict = {}
        ko_names = [float('NaN') for i in range(population_size)]
        for ko_no in range(population_size):
            length_of_combo = random.randint(newGen_params_dict['min_ko_set_size'], newGen_params_dict['max_ko_set_size'])
            ko_names[ko_no] = 'ko_set' + str(ko_no + 1)
            ko_idxs = self.random_combination(all_possible_idxs_iter, length_of_combo)
            # convert indexs into gene IDs
            ko_ids = [idx_to_ids_dict[idx] for idx in ko_idxs]
            ko_ids.sort() # this should be taken care of but to be safe always try and keep gene IDs in ascending order to avoid unforseen problems

            # convert gene IDs into codes
            ko_codes = [gene_id_to_code_dict[ID] for ID in ko_ids]
            ko_name_to_set_dict[ko_names[ko_no]] = tuple(ko_codes)

        # return must take the form of child_name_to_genome_dict
        # so convert kos to genomes
        #child_name_to_genome_dict = {ko_name: tuple([id_to_idx_dict[gene_code_to_id_dict[gene_code]] for gene_code in ko_set]) for ko_name, ko_set in ko_name_to_set_dict.items()}
        child_name_to_genome_dict = {ko_name: tuple([0 if self.id_to_code_dict[idx_to_ids_dict[idx]] in ko_set else 1 for idx in range(len(idx_to_ids_dict))]) for ko_name, ko_set in ko_name_to_set_dict.items()}

        return child_name_to_genome_dict

