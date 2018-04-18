import sys
sys.path.insert(0, '/home/oli/git/published_libraries/computer_communication_framework')
from computer_communication_framework.base_mga import GeneticAlgorithmBase
from job_management import SubmissionKarr2012, SubmissionManagerKarr2012

class Karr2012GenomeReductionGeneticAlgorithm(Karr2012MgaBase, GeneticAlgorithmBase):
    def __init__(self):
        pass

class Karr2012GeneticAlgorithmBase(GeneticAlgorithmBase, Karr2012MgaBase):
    def __init__(self, dict_of_cluster_instances, MGA_name, relative2clusterBasePath_simulation_output_path, repetitions_of_a_unique_simulation, checkStopFunction, getNewGenerationFunction, getGenerationNameFunction):
	GeneticAlgorithmBase.__init__(dict_of_cluster_instances, MGA_name, relative2clusterBasePath_simulation_output_path, repetitions_of_a_unique_simulation, checkStopFunction, getNewGenerationFunction)
	Karr2012MgaBase.__init__()
        self.getGenerationNameFunction = getGenerationNameFunction

    def createJobSubmissionInstance(self, cluster_conn, single_child_name_to_set_dict):
        submission_name = self.MGA_name + '_' + self.getGenerationNameFunction()
        cluster_connection = cluster_conn
        ko_name_to_set_dict = single_child_name_to_set_dict
        simulation_output_path = cluster_connection.base_output_path + '/' + self.relative2clusterBasePath_simulation_output_path + '/' + self.MGA_name + '/' + self.getGenerationNameFunction()
        errorfile_path = cluster_connection.base_output_path + '/' + self.relative2clusterBasePath_simulation_output_path + '/' + self.MGA_name + '/' + self.getGenerationNameFunction()
        outfile_path = cluster_connection.base_output_path + '/' + self.relative2clusterBasePath_simulation_output_path + '/' + self.MGA_name + '/' + self.getGenerationNameFunction()
        runfiles_path = self.base_runfiles_path + '/' + self.relative2clusterBasePath_simulation_output_path + '/' + self.MGA_name + '/' + self.getGenerationNameFunction()
        master_dir = self.wholecell_master_dir
        updateCentralDbFunction = 
        convertDataFunction = 
        data_conversion_command_code = 

        job_submission_inst = SubmissionKarr2012(submission_name, cluster_connection, ko_name_to_set_dict, simulation_output_path, errorfile_path, outfile_path, runfiles_path, repeitions_of_unique_task, master_dir, SubmissionKarr2012.updateCentralDbFunction, convertDataFunction, data_conversion_command_code, 3600, 900, '/space/oc13378/myprojects/github/uob/wc/mg/oc2/whole_cell_modelling_suite/tmp_storage')

class Karr2012MgaBase():
    """
    This only a suite a methods that MGAs might use when operating on the Karr et al. 2012 whole-cell model.
    """
    
    def __init__(self):
        pass

    ### FUNCTIONS TO GET GENERATION NAMES

    def getGenerationNameSimple(self):
        """
        Gives a name for a generation in the form of:
            generation_name = 'gen' + str(self.generation_counter)

        Returns:
            generation_name (str): A simple name for the current generation.
        """

        generation_name = 'gen' + str(self.generation_counter)

        return generation_name

    ### FUNCTIONS TO GET THE POPULATION SIZE

    def getPopulationSizeFromDict(self):
        """
        Returns the size of the current generation. The MGA that uses this function must have a class variable called self.generation_num_to_gen_size_dict where the keys are generation numbers and the value corresponds the size of that generation. If there is not a key equal to the current generation then self.generation_num_to_gen_size_dict[-1] will be used.

        Returns:
            generation_size (int): The number of children to be created in the current generation.
        """
        
        important_generation_numbers = list(self.generation_num_to_gen_size_dict.keys())
        if important_generation_numbers.count(self.generation_counter) > 0:
                generation_size = self.generation_num_to_gen_size_dict[self.generation_counter]
        else:   
                generation_size = self.generation_num_to_gen_size_dict[-1]

        return generation_size

    ### FUNCTIONS TO GENERATE SETS OF CHILDREN

    def getRandomKos(self):
	submission_name = self.getGenerationNameFunction()
	population_size = self.getPopulationSizeFunction()
	# get gene code to gene ID dictionary for every possible gene that we want to pick from
	gene_code_to_id_dict = self.gene_code_to_id_dict.copy()
	# In the "genome form" we need to map the index of the genome to a gene ID.
	idx_to_ids_dict = self.createIdxToIdDict(gene_code_to_id_dict)
	list_of_ids = list(gene_code_to_id_dict.values())
	list_of_ids.sort()
	all_possible_idxs_iter = range(len(list_of_ids))
	# create the inverse dictionary
	gene_id_to_code_dict = self.invertDictionary(gene_code_to_id_dict)
	ko_name_to_set_dict = {}
	ko_names = [float('NaN') for i in range(population_size)]
	for ko_no in range(population_size):
	    length_of_combo = random.randint(2, 5)
	    ko_names[ko_no] = 'ko' + str(ko_no + 1)
	    ko_idxs = self.random_combination(all_possible_idxs_iter, length_of_combo)
	    # convert indexs into gene IDs
	    ko_ids = [idx_to_ids_dict[idx] for idx in ko_idxs]
	    ko_ids.sort() # this should be taken care of but to be safe always try and keep gene IDs in ascending order to avoid unforseen problems

	    # convert gene IDs into codes
	    ko_codes = [gene_id_to_code_dict[id] for id in ko_ids]
	    ko_name_to_set_dict[ko_names[ko_no]] = tuple(ko_codes)

	return ko_name_to_set_dict

    # All the following methods are static because they are common tools and it is useful to be able to access them wihtout creating an instance.

    # STATIC METHODS
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

