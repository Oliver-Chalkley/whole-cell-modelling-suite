from abc import ABCMeta, abstractmethod
import sys
sys.path.insert(0, '/home/oli/git/published_libraries/computer_communication_framework')
from computer_communication_framework.base_connection import BasePbs, BaseSlurm
import subprocess
import re
import datetime
import pandas as pd
import pathlib

class Bg(BaseSlurm):
    """
    Because this initialises it's parents and it's grandparents class and so in addition to the following arguments you will also have to pass the arguments to satisfy the parent and grandparent classes.

    This is one of the final layers of te connection classes. The purpose of this layer is to contain all the methods and variables that relate only to the whole-cell model jobs related to BlueCrystal Phase III.

    Args:
        path_to_flex1 (str): Flex1 is a disk that the Minimal genome group uses as the main read/write disk for the Bristol supercomputers and also for the storage of communal data and databases etc. If a cluster does not have direct access to flex1 one then a class needs to be written without the path_to_flex1 variable and a cluster connection needs to be passed as the db_connection variable.
        relative_to_flex1_path_to_communual_data (str): The communual data directory can be found at path_to_flex1/relative_to_flex1_path_to_communual_data

    NOTE: The instance variable self.db_connection = self may seem confusing and so will be explained here. If one has access to an off campus cluster then that will not have access to the communual data on Flex1. In order to give off-campus access to the communual data we created a self.db_connection instance variable which needs to be a connection that has direct access to the data. Obviously connections that already have direct access don't NEED the self.db_connection variable but in order to be consistent so that higher level programs know where to access this data we also create the variable for connections with direct access and simply pass itself to that variable.
    """

    def __init__(self, cluster_user_name, ssh_config_alias, forename_of_user, surname_of_user, user_email, base_output_path, base_runfiles_path, affiliation, max_array_size = 200):
        BaseSlurm.__init__(self, cluster_user_name, ssh_config_alias, forename_of_user, surname_of_user, user_email, base_output_path, base_runfiles_path, 'BlueGem: BrisSynBio, Advanced Computing Research Centre, University of Bristol.', max_array_size, affiliation, slurm_account_name = 'Flex1')

    def checkDiskUsage(self):
        # Not had desperate need for this but it should definitely be added!
        pass

class Bc3(BasePbs):
    """
    Because this initialises it's parents and it's grandparents class and so in addition to the following arguments you will also have to pass the arguments to satisfy the parent and grandparent classes.

    This is one of the final layers of te connection classes. The purpose of this layer is to contain all the methods and variables that relate only to the whole-cell model jobs related to BlueCrystal Phase III.

    Args:
        path_to_flex1 (str): Flex1 is a disk that the Minimal genome group uses as the main read/write disk for the Bristol supercomputers and also for the storage of communal data and databases etc. If a cluster does not have direct access to flex1 one then a class needs to be written without the path_to_flex1 variable and a cluster connection needs to be passed as the db_connection variable.
        relative_to_flex1_path_to_communual_data (str): The communual data directory can be found at path_to_flex1/relative_to_flex1_path_to_communual_data

    NOTE: The instance variable self.db_connection = self may seem confusing and so will be explained here. If one has access to an off campus cluster then that will not have access to the communual data on Flex1. In order to give off-campus access to the communual data we created a self.db_connection instance variable which needs to be a connection that has direct access to the data. Obviously connections that already have direct access don't NEED the self.db_connection variable but in order to be consistent so that higher level programs know where to access this data we also create the variable for connections with direct access and simply pass itself to that variable.
    """

    def __init__(self, cluster_user_name, ssh_config_alias, forename_of_user, surname_of_user, user_email, base_output_path, base_runfiles_path, affiliation, max_array_size = 500):
        BasePbs.__init__(self, cluster_user_name, ssh_config_alias, forename_of_user, surname_of_user, user_email, base_output_path, base_runfiles_path, 'BlueCrystal Phase 3: Advanced Computing Research Centre, University of Bristol.', max_array_size, affiliation)

    def checkDiskUsage(self):
        """
        This function returns disk usage details. BC3 uses the command pan_quota in order to get a users disk quota, here we use sed, awk, head, and tail to extract the hard limit, soft limit, usage and the units.
                
        Returns:
            output_dict (dict): Has keys usage, soft_limit, hard_limit and units.
        """

        # create all the post connection commands needed
        get_disk_usage_units_command = "pan_quota | awk \'{print $1}\' | tail -n 2 | head -n 1 | sed \'s/[<>]//g\'"
        get_disk_usage_command = "pan_quota | awk \'{print $1}\' | tail -n 1"
        get_disk_usage_soft_limit_command = "pan_quota | awk \'{print $2}\' | tail -n 1"
        get_disk_usage_hard_limit_command = "pan_quota | awk \'{print $3}\' | tail -n 1"
        # combine the connection command with the post connection commands in a list (as is recomended).
        units_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_units_command]
        usage_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_command]
        soft_limit_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_soft_limit_command]
        hard_limit_cmd = ["ssh", self.ssh_config_alias, get_disk_usage_hard_limit_command]
        # send the commands and save the exit codes and outputs
        units = self.localShellCommand(units_cmd)
        usage = self.localShellCommand(usage_cmd)
        soft_limit = self.localShellCommand(soft_limit_cmd)
        hard_limit = self.localShellCommand(hard_limit_cmd)
        # convert string outputs to floats where neccessary
        units[1] = str(units[1], "utf-8").rstrip()
        usage[1] = float(usage[1])
        soft_limit[1] = float(soft_limit[1])
        hard_limit[1] = float(hard_limit[1])
        # print some stats
        print(100 * (usage[1] / (1.0 * hard_limit[1]) ),"% of total disk space used.\n\n",hard_limit[1] - usage[1]," ",units[1]," left until hard limit.\n\n",soft_limit[1] - usage[1]," ",units[1]," left unit soft limit.", sep='')
        
        output_dict = {'usage': usage, 'soft_limit': soft_limit, 'hard_limit': hard_limit, 'units': units}

        return output_dict

class Karr2012General(metaclass=ABCMeta):
    """
    Contains all the attributes neccessary for connection class that wants to interact with infra-structure created by Oliver Chalkley for the Whole-Cell model (Karr et al. 2012).
    """

    def __init__(self, wholecell_master_dir, activate_virtual_environment_list, path_to_flex1, relative_to_flex1_path_to_communual_data, db_connection):
        self.wholecell_master_dir = wholecell_master_dir
        self.activate_virtual_environment_list = activate_virtual_environment_list
        self.path_to_flex1 = path_to_flex1
        self.relative_to_flex1_path_to_communual_data = relative_to_flex1_path_to_communual_data
        self.path_to_database_dir = self.path_to_flex1 + '/'  + self.relative_to_flex1_path_to_communual_data
        self.db_connection = db_connection
        self.initial_message_in_code = "# This script was automatically created by Oliver Chalkley's whole-cell modelling suite. Please contact on o.chalkley@bristol.ac.uk\n"

    def getAllProteinGroups(self, gene_info_df, gene_code):
        list_of_protein_groups = eval('[\'' + "', '".join(gene_info_df['functional_unit'].loc[gene_code].split(", ")) + '\']')
        return list_of_protein_groups

    def getGeneInfoDf(self, tuple_of_gene_codes):
        dict_out = self.getGeneInfoDict(tuple_of_gene_codes)
        gene_info = pd.DataFrame(dict_out)
        gene_info = gene_info.set_index('code')

        return gene_info
                
    def getNotJr358Genes(self):
        all_genes_raw = self.db_connection.sendSqlToStaticDb('select code from genes')
        # output comes as a list of return code and stdout as a string (list of tuples). Check return is zero and format the string so it is an actual python object and then turn that into a easily usable list.
        if all_genes_raw['return_code'] == 0:
            sql_out = eval(all_genes_raw['stdout'].strip())
            all_codes = set([code[0] for code in sql_out])

        else:
            raise ValueError('Data retrieval from static.db failed with exit code: ', all_genes_raw)

        # get JR358
        jr358 = set(self.getJr358Genes())
        removed_genes = all_codes.difference(jr358)

        return tuple(removed_genes)

    def getGeneInfoDict(self, tuple_of_gene_codes):
        """
        NOTE: It is advised that you use this data through the analysis part of the library as this is a bit raw.
        
        This function takes a tuple of gene codes and returns some information about their function and their single gene essentiality in a dictionary. The raw output from the database is retrieved from the 'self.useStaticDbFunction' function and processed here.

        Args:
            tuple_of_gene_codes (tuple of strings): Each string is a gene-code as dictated by Karr et al. 2012.

        Returns:
            gene_info (dict): A dictionary with keys 'code', 'type', 'name', 'symbol', 'functional_unit', 'deletion_phenotype', 'essential_in_model', 'essential_in_experiment'.
        """

        raw_out = self.useStaticDbFunction([tuple_of_gene_codes], 'CodeToInfo')
        if raw_out['return_code'] == 0:
            as_list = eval(raw_out['stdout'].strip())
            list_of_column_names = ['code', 'type', 'name', 'symbol', 'functional_unit', 'deletion_phenotype', 'essential_in_model', 'essential_in_experiment']
            gene_info = {list_of_column_names[name_idx]: [as_list[element_idx][name_idx] for element_idx in range(len(as_list))] for name_idx in range(len(list_of_column_names))}
        else:
            raise ValueError("Failed to retrieve sql data. Query returned: ", raw_out)

        return gene_info

    def useStaticDbFunction(self, list_of_function_inputs, function_call):
        """
        This function allows you to a call a pre-made function from the static.db io library so that you can quickly and easily retrieve data whilst keeping code to a minimum.

        Args:
            function_call (str): The name of the function in the static.db io library that you wish to use.
            list_of_function_inputs (list of unknown contents): This is a list of the arguments that need to be passed to the 'function_call' function.
            path_to_staticDb_stuff (str): path to the staticDB directory.
        """

        path_to_staticDb_stuff = self.path_to_flex1 +'/' + self.relative_to_flex1_path_to_communual_data + '/staticDB'
        add_anoconda_module = self.activate_virtual_environment_list[0]
        activate_virtual_environment = self.activate_virtual_environment_list[1]
        change_to_lib_dir = 'cd ' + path_to_staticDb_stuff
        get_data = 'python -c "from staticDB import io as sio;static_db_conn = sio();print(static_db_conn.' + function_call + '(' + ','.join(map(str, list_of_function_inputs)) + '))"'
        cmd = add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_data
        cmd_list = [add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_data]
        raw_out = self.remoteConnection(cmd_list)

        return raw_out


    def sendSqlToStaticDb(self, sql_command):
        """
        Takes an SQLITE3 command as a string and sends it to static.db and returns the raw output.

        Args:
            sql_command (str): SQLITE3 command that needs to be executed on the static database.
            path_to_staticDb_stuff (str): Path to the staticDB directory.

        Returns:
            raw_out (??): Raw output from the Connection.getOutput function.
        """
        path_to_staticDb_stuff = self.path_to_flex1 +'/' + self.relative_to_flex1_path_to_communual_data + '/staticDB'
        add_anoconda_module = 'module add languages/python-anaconda-4.2-3.5'
        activate_virtual_environment = 'source activate wholecell_modelling_suite'
        change_to_lib_dir = 'cd ' + path_to_staticDb_stuff
        get_data = 'python -c "from staticDB import io as sio;static_db_conn = sio();print(static_db_conn.raw_sql_query(\'' + sql_command + '\'))"'
        cmd = add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_data
        cmd_list = [add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_data]
        raw_out = self.remoteConnection(cmd_list)

        return raw_out

    def convertGeneCodeToId(self, tuple_of_gene_codes):
        """
        Takes a tuple of genes code and returns a dictionary of codes to corresponding gene IDs.

        Args:
            tuple_of_genes (tuple of strings): Each string is a gene code as dictated by Karr et al. 2012.
            path_to_staticDb_stuff (str): The path to the staticDB directory.

        Returns:
           code_to_id_dict (dict): Each key is a gene code and is correspponding value is the ID that represents the gene code in the static database. 
        """

        if type(tuple_of_gene_codes) is not tuple:
                raise TypeException('Gene codes must be a tuple (even if only 1! i.e. single_tuple = (\'MG_001\',)) here type(tuple_of_gene_codes)=', type(tuple_of_gene_codes))
        path_to_staticDb_stuff = self.path_to_flex1 +'/' + self.relative_to_flex1_path_to_communual_data + '/staticDB'
        add_anoconda_module = self.activate_virtual_environment_list[0]
        activate_virtual_environment = self.activate_virtual_environment_list[1]
        change_to_lib_dir = 'cd ' + path_to_staticDb_stuff
        get_gene_id = 'python -c "from staticDB import io as sio;static_db_conn = sio();print(static_db_conn.CodeToId(' + str(tuple_of_gene_codes) + '))"'
        cmd = add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_gene_id
        cmd_list = [add_anoconda_module + ";" + activate_virtual_environment + ";" + change_to_lib_dir + ";" + get_gene_id]
        raw_out = self.remoteConnection(cmd_list)

        # send command and get output
        output = eval(raw_out['stdout'].strip())
        # it doesn't output the answer in the order you input it so we need to make a dictionary
        code_to_id_dict = {}
        for out in output:
            code_to_id_dict[out[1]] = out[0]

        return code_to_id_dict

    def getJr358Genes(self):
        """The function returns the 358 genes that Joshua Rees classified for potential KOs."""
        return ('MG_001', 'MG_003', 'MG_004', 'MG_005', 'MG_006', 'MG_007', 'MG_008', 'MG_009', 'MG_012', 'MG_013', 'MG_014', 'MG_015', 'MG_019', 'MG_020', 'MG_021', 'MG_022', 'MG_023', 'MG_026', 'MG_027', 'MG_029', 'MG_030', 'MG_031', 'MG_033', 'MG_034', 'MG_035', 'MG_036', 'MG_037', 'MG_038', 'MG_039', 'MG_040', 'MG_041', 'MG_042', 'MG_043', 'MG_044', 'MG_045', 'MG_046', 'MG_047', 'MG_048', 'MG_049', 'MG_050', 'MG_051', 'MG_052', 'MG_053', 'MG_055', 'MG_473', 'MG_058', 'MG_059', 'MG_061', 'MG_062', 'MG_063', 'MG_064', 'MG_065', 'MG_066', 'MG_069', 'MG_070', 'MG_071', 'MG_072', 'MG_073', 'MG_075', 'MG_077', 'MG_078', 'MG_079', 'MG_080', 'MG_081', 'MG_082', 'MG_083', 'MG_084', 'MG_085', 'MG_086', 'MG_087', 'MG_088', 'MG_089', 'MG_090', 'MG_091', 'MG_092', 'MG_093', 'MG_094', 'MG_097', 'MG_098', 'MG_099', 'MG_100', 'MG_101', 'MG_102', 'MG_476', 'MG_104', 'MG_105', 'MG_106', 'MG_107', 'MG_109', 'MG_110', 'MG_111', 'MG_112', 'MG_113', 'MG_114', 'MG_118', 'MG_119', 'MG_120', 'MG_121', 'MG_122', 'MG_123', 'MG_124', 'MG_126', 'MG_127', 'MG_128', 'MG_130', 'MG_132', 'MG_136', 'MG_137', 'MG_139', 'MG_141', 'MG_142', 'MG_143', 'MG_145', 'MG_149', 'MG_150', 'MG_151', 'MG_152', 'MG_153', 'MG_154', 'MG_155', 'MG_156', 'MG_157', 'MG_158', 'MG_159', 'MG_160', 'MG_161', 'MG_162', 'MG_163', 'MG_164', 'MG_165', 'MG_166', 'MG_167', 'MG_168', 'MG_169', 'MG_170', 'MG_171', 'MG_172', 'MG_173', 'MG_174', 'MG_175', 'MG_176', 'MG_177', 'MG_178', 'MG_179', 'MG_180', 'MG_181', 'MG_182', 'MG_183', 'MG_184', 'MG_186', 'MG_187', 'MG_188', 'MG_189', 'MG_190', 'MG_191', 'MG_192', 'MG_194', 'MG_195', 'MG_196', 'MG_197', 'MG_198', 'MG_200', 'MG_201', 'MG_203', 'MG_204', 'MG_205', 'MG_206', 'MG_208', 'MG_209', 'MG_210', 'MG_481', 'MG_482', 'MG_212', 'MG_213', 'MG_214', 'MG_215', 'MG_216', 'MG_217', 'MG_218', 'MG_221', 'MG_224', 'MG_225', 'MG_226', 'MG_227', 'MG_228', 'MG_229', 'MG_230', 'MG_231', 'MG_232', 'MG_234', 'MG_235', 'MG_236', 'MG_238', 'MG_239', 'MG_240', 'MG_244', 'MG_245', 'MG_249', 'MG_250', 'MG_251', 'MG_252', 'MG_253', 'MG_254', 'MG_257', 'MG_258', 'MG_259', 'MG_261', 'MG_262', 'MG_498', 'MG_264', 'MG_265', 'MG_266', 'MG_270', 'MG_271', 'MG_272', 'MG_273', 'MG_274', 'MG_275', 'MG_276', 'MG_277', 'MG_278', 'MG_282', 'MG_283', 'MG_287', 'MG_288', 'MG_289', 'MG_290', 'MG_291', 'MG_292', 'MG_293', 'MG_295', 'MG_297', 'MG_298', 'MG_299', 'MG_300', 'MG_301', 'MG_302', 'MG_303', 'MG_304', 'MG_305', 'MG_309', 'MG_310', 'MG_311', 'MG_312', 'MG_315', 'MG_316', 'MG_317', 'MG_318', 'MG_321', 'MG_322', 'MG_323', 'MG_324', 'MG_325', 'MG_327', 'MG_329', 'MG_330', 'MG_333', 'MG_334', 'MG_335', 'MG_517', 'MG_336', 'MG_339', 'MG_340', 'MG_341', 'MG_342', 'MG_344', 'MG_345', 'MG_346', 'MG_347', 'MG_349', 'MG_351', 'MG_352', 'MG_353', 'MG_355', 'MG_356', 'MG_357', 'MG_358', 'MG_359', 'MG_361', 'MG_362', 'MG_363', 'MG_522', 'MG_365', 'MG_367', 'MG_368', 'MG_369', 'MG_370', 'MG_372', 'MG_375', 'MG_376', 'MG_378', 'MG_379', 'MG_380', 'MG_382', 'MG_383', 'MG_384', 'MG_385', 'MG_386', 'MG_387', 'MG_390', 'MG_391', 'MG_392', 'MG_393', 'MG_394', 'MG_396', 'MG_398', 'MG_399', 'MG_400', 'MG_401', 'MG_402', 'MG_403', 'MG_404', 'MG_405', 'MG_407', 'MG_408', 'MG_409', 'MG_410', 'MG_411', 'MG_412', 'MG_417', 'MG_418', 'MG_419', 'MG_421', 'MG_424', 'MG_425', 'MG_426', 'MG_427', 'MG_428', 'MG_429', 'MG_430', 'MG_431', 'MG_433', 'MG_434', 'MG_435', 'MG_437', 'MG_438', 'MG_442', 'MG_444', 'MG_445', 'MG_446', 'MG_447', 'MG_448', 'MG_451', 'MG_453', 'MG_454', 'MG_455', 'MG_457', 'MG_458', 'MG_460', 'MG_462', 'MG_463', 'MG_464', 'MG_465', 'MG_466', 'MG_467', 'MG_468', 'MG_526', 'MG_470')
class Karr2012BgTest(Bg, Karr2012General):
    """
    """

    def __init__(self, cluster_user_name, ssh_config_alias, forename_of_user, surname_of_user, user_email, base_output_path, base_runfiles_path, wholecell_master_dir, affiliation = 'Genome Design Group, Bristol Centre for Complexity Science, BrisSynBio, University of Bristol.', activate_virtual_environment_list = ['module add apps/anaconda3-2.3.0', 'source activate whole_cell_modelling_suite'], path_to_flex1 = '/projects/flex1', relative_to_flex1_path_to_communual_data = 'database'):
        Bg.__init__(self, cluster_user_name, ssh_config_alias, forename_of_user, surname_of_user, user_email, base_output_path, base_runfiles_path, affiliation)
        self.db_connection = self
        Karr2012General.__init__(self, wholecell_master_dir, activate_virtual_environment_list, path_to_flex1, relative_to_flex1_path_to_communual_data, self.db_connection)

    def createUnittestScript(self, submission_data_dict, no_file_overwrite = True):
        #### FIXED I THINK: JUST COPIED ANDPASTED FROM BC3 VERSION SO NEED TO CHANGE STILL!!!!
        # unpack the dictionary
        tmp_save_path = submission_data_dict['tmp_save_path']
        name_of_job = submission_data_dict['name_of_job']
        unittest_master_dir = submission_data_dict['unittest_master_dir']
        output_dir = submission_data_dict['output_dir']
        outfiles_path = submission_data_dict['outfiles_path']
        errorfiles_path = submission_data_dict['errorfiles_path']
        no_of_unique_ko_sets = submission_data_dict['no_of_unique_ko_sets']
        no_of_repetitions_of_each_ko = submission_data_dict['no_of_repetitions_of_each_ko']
        queue_name = submission_data_dict['queue_name']

        submission_script_filename = tmp_save_path + '/' + name_of_job + '_submission.sh'
        # raise exception if the file already exists
        with pathlib.Path(submission_script_filename) as test_file:
            if test_file.is_file():
                raise ValueError(submission_script_filename + ' already exists!')
        
        # assign None so that we can check things worked later
        job_array_numbers = None
        # The maximum job array size on BC3
        max_job_array_size = 200
        # initialise output dict
        output_dict = {}
        # test that a reasonable amount of jobs has been submitted (This is not a hard and fast rule but there has to be a max and my intuition suggestss that it will start to get complicated around this level i.e. queueing and harddisk space etc)
        total_sims = no_of_unique_ko_sets * no_of_repetitions_of_each_ko
        if total_sims > 20000:
                raise ValueError('Total amount of simulations for one batch submission must be less than 20,000, here total_sims=',total_sims)

        output_dict['total_sims'] = total_sims
        # spread simulations across array jobs
        if no_of_unique_ko_sets <= max_job_array_size:
                no_of_unique_ko_sets_per_array_job = 1
                no_of_arrays = no_of_unique_ko_sets
                job_array_numbers = '1-' + str(no_of_unique_ko_sets)
                walltime = '00:00:10'
        else:
                # job_array_size * no_of_unique_ko_sets_per_array_job = no_of_unique_ko_sets so all the factors of no_of_unique_ko_sets is
                common_factors = [x for x in range(1, no_of_unique_ko_sets+1) if no_of_unique_ko_sets % x == 0]
                # make the job_array_size as large as possible such that it is less than max_job_array_size
                factor_idx = len(common_factors) - 1
                while factor_idx >= 0:
                        if common_factors[factor_idx] < max_job_array_size:
                                job_array_numbers = '1-' + str(common_factors[factor_idx])
                                no_of_arrays = common_factors[factor_idx]
                                no_of_unique_ko_sets_per_array_job = common_factors[(len(common_factors)-1) - factor_idx]
                                factor_idx = -1
                        else:
                                factor_idx -= 1

                # raise error if no suitable factors found!
                if job_array_numbers is None:
                        raise ValueError('job_array_numbers should have been assigned by now! This suggests that it wasn\'t possible for my algorithm to split the KOs across the job array properly. Here no_of_unique_ko_sets=', no_of_unique_ko_sets, ' and the common factors of this number are:', common_factors)

                # add some time to the walltime because I don't think the jobs have to startat the same time
                walltime = '00:00:10'

        output_dict['no_of_arrays'] = no_of_arrays
        output_dict['no_of_unique_kos_per_array_job'] = no_of_unique_ko_sets_per_array_job
        output_dict['no_of_repetitions_of_each_ko'] = no_of_repetitions_of_each_ko
        # calculate the amount of cores per array job - NOTE: for simplification we only use cores and not nodes (this is generally the fastest way to get through the queue anyway)
        no_of_cores = no_of_repetitions_of_each_ko * no_of_unique_ko_sets_per_array_job
        output_dict['no_of_sims_per_array_job'] = no_of_cores
        output_dict['list_of_rep_dir_names'] = list(range(1, no_of_repetitions_of_each_ko + 1))
        no_of_nodes = 1

        # We use the standard submission script template inherited form the Pbs class and then add the following code to the bottom of it
        list_of_job_specific_code = self.activate_virtual_environment_list.copy()
        list_of_job_specific_code += ["master=" + unittest_master_dir + "\n", "# create output directory", "base_outDir=" + output_dir + "\n", "# go to master directory", "cd ${master}" + "\n", "python unittest_model.py " + output_dir]

        # get the standard submission script
        standard_submission_script = self.createSubmissionScriptTemplate(name_of_job, no_of_nodes, no_of_cores, job_array_numbers, walltime, queue_name, outfiles_path, errorfiles_path, slurm_account_name = 'Flex1', initial_message_in_code = "# This script was automatically created by Oli      ver Chalkley's whole-cell modelling suite. Please contact on o.chalkley@bristol.ac.uk\n", shebang = "#!/bin/bash -login\n")

        self.createStandardSubmissionScript(submission_script_filename, standard_submission_script + list_of_job_specific_code)

        output_dict['submission_script_filename'] = submission_script_filename

        return output_dict

    def createWcmKoScript(self, submission_data_dict):

        # unpack the dictionary
        tmp_save_path = submission_data_dict['tmp_save_path']
        name_of_job = submission_data_dict['name_of_job']
        wholecell_model_master_dir = submission_data_dict['wholecell_model_master_dir']
        output_dir = submission_data_dict['output_dir']
        outfiles_path = submission_data_dict['outfiles_path']
        errorfiles_path = submission_data_dict['errorfiles_path']
        path_and_name_of_ko_codes = submission_data_dict['path_and_name_of_ko_codes']
        path_and_name_of_unique_ko_dir_names = submission_data_dict['path_and_name_of_unique_ko_dir_names']
        no_of_unique_ko_sets = len(submission_data_dict['ko_name_to_set_dict'])
        no_of_repetitions_of_each_ko = submission_data_dict['no_of_repetitions_of_each_ko']
        queue_name = submission_data_dict['queue_name']

        submission_script_filename = tmp_save_path + '/' + name_of_job + '_submission.sh'
        # assign None so that we can check things worked later
        job_array_numbers = None
        # The maximum job array size on BC3
        max_job_array_size = 200
        # initialise output dict
        output_dict = {}
        # test that a reasonable amount of jobs has been submitted (This is not a hard and fast rule but there has to be a max and my intuition suggestss that it will start to get complicated around this level i.e. queueing and harddisk space etc)
        total_sims = no_of_unique_ko_sets * no_of_repetitions_of_each_ko
        if total_sims > 20000:
                raise ValueError('Total amount of simulations for one batch submission must be less than 20,000, here total_sims=',total_sims)

        output_dict['total_sims'] = total_sims
        # spread simulations across array jobs
        if no_of_unique_ko_sets <= max_job_array_size:
                no_of_unique_ko_sets_per_array_job = 1
                no_of_arrays = no_of_unique_ko_sets
                job_array_numbers = '1-' + str(no_of_unique_ko_sets)
                walltime = '0-30:00:00'
        else:
                # job_array_size * no_of_unique_ko_sets_per_array_job = no_of_unique_ko_sets so all the factors of no_of_unique_ko_sets is
                common_factors = [x for x in range(1, no_of_unique_ko_sets+1) if no_of_unique_ko_sets % x == 0]
                # make the job_array_size as large as possible such that it is less than max_job_array_size
                factor_idx = len(common_factors) - 1
                while factor_idx >= 0:
                        if common_factors[factor_idx] < max_job_array_size:
                                job_array_numbers = '1-' + str(common_factors[factor_idx])
                                no_of_arrays = common_factors[factor_idx]
                                no_of_unique_ko_sets_per_array_job = common_factors[(len(common_factors)-1) - factor_idx]
                                factor_idx = -1
                        else:
                                factor_idx -= 1

                # raise error if no suitable factors found!
                if job_array_numbers is None:
                        raise ValueError('job_array_numbers should have been assigned by now! This suggests that it wasn\'t possible for my algorithm to split the KOs across the job array properly. Here no_of_unique_ko_sets=', no_of_unique_ko_sets, ' and the common factors of this number are:', common_factors)

                # add some time to the walltime because I don't think the jobs have to startat the same time
                walltime = '30:00:00'

        output_dict['no_of_arrays'] = no_of_arrays
        output_dict['no_of_unique_kos_per_array_job'] = no_of_unique_ko_sets_per_array_job
        output_dict['no_of_repetitions_of_each_ko'] = no_of_repetitions_of_each_ko
        # calculate the amount of cores per array job - NOTE: for simplification we only use cores and not nodes (this is generally the fastest way to get through the queue anyway)
        no_of_cores = no_of_repetitions_of_each_ko * no_of_unique_ko_sets_per_array_job
        output_dict['no_of_sims_per_array_job'] = no_of_cores
        output_dict['list_of_rep_dir_names'] = list(range(1, no_of_repetitions_of_each_ko + 1))
        no_of_nodes = 1

        # We use the standard submission script template inherited form the Pbs class and then add the following code to the bottom of it
        list_of_job_specific_code = ["# load required modules", "module load apps/matlab-r2013a", 'echo "Modules loaded:"', "module list\n", "# create the master directory variable", "master=" + wholecell_model_master_dir + "\n", "# create output directory", "base_outDir=" + output_dir + "\n", "# collect the KO combos", "ko_list=" + path_and_name_of_ko_codes, "ko_dir_names=" + path_and_name_of_unique_ko_dir_names + "\n", "# Get all the gene KOs and output folder names", 'for i in `seq 1 ' + str(no_of_unique_ko_sets_per_array_job) + '`', 'do', '    Gene[${i}]=$(awk NR==$((' + str(no_of_unique_ko_sets_per_array_job) + '*(${PBS_ARRAYID}-1)+${i})) ${ko_list})', '    unique_ko_dir_name[${i}]=$(awk NR==$((' + str(no_of_unique_ko_sets_per_array_job) + '*(${PBS_ARRAYID}-1)+${i})) ${ko_dir_names})', "done" + "\n", "# go to master directory", "cd ${master}" + "\n", "# NB have limited MATLAB to a single thread", 'options="-nodesktop -noFigureWindows -nosplash -singleCompThread"' + "\n", "# run 16 simulations in parallel", 'echo "Running simulations (single threaded) in parallel - let\'s start the timer!"', 'start=`date +%s`' + "\n", "# create all the directories for the diarys (the normal output will be all mixed up cause it's in parrallel!)", 'for i in `seq 1 ' + str(no_of_unique_ko_sets_per_array_job) + '`', "do", '    for j in `seq 1 ' + str(no_of_repetitions_of_each_ko) + '`', "    do", '        specific_ko="$(echo ${Gene[${i}]} | sed \'s/{//g\' | sed \'s/}//g\' | sed \"s/\'//g\" | sed \'s/\"//g\' | sed \'s/,/-/g\')/${j}"', '        mkdir -p ${base_outDir}/${unique_ko_dir_name[${i}]}/diary${j}', '        matlab ${options} -r "diary(\'${base_outDir}/${unique_ko_dir_name[${i}]}/diary${j}/diary.out\');addpath(\'${master}\');setWarnings();setPath();runSimulation(\'runner\',\'koRunner\',\'logToDisk\',true,\'outDir\',\'${base_outDir}/${unique_ko_dir_name[${i}]}/${j}\',\'jobNumber\',$((no_of_repetitions_of_each_ko*no_of_unique_ko_sets_per_array_job*(${PBS_ARRAYID}-1)+no_of_unique_ko_sets_per_array_job*(${i}-1)+${j})),\'koList\',{{${Gene[${i}]}}});diary off;exit;" &', "    done", "done", "wait" + "\n", "end=`date +%s`", "runtime=$((end-start))", 'echo "$((${no_of_unique_ko_sets_per_array_job}*${no_of_repetitions_of_each_ko})) simulations took: ${runtime} seconds."']

        # get the standard submission script
        standard_submission_script = self.createSubmissionScriptTemplate(name_of_job, no_of_nodes, no_of_cores, job_array_numbers, walltime, queue_name, outfiles_path, errorfiles_path, slurm_account_name = 'Flex1', initial_message_in_code = "# This script was automatically created by Oliver Chalkley's whole-cell modelling suite. Please contact on o.chalkley@bristol.ac.uk\n", shebang = "#!/bin/bash -login\n")

        self.createStandardSubmissionScript(submission_script_filename, standard_submission_script + list_of_job_specific_code)

        output_dict['submission_script_filename'] = submission_script_filename

        return output_dict

class Karr2012Bg(Bg, Karr2012General):
    def __init__(self, cluster_user_name, ssh_config_alias, forename_of_user, surname_of_user, user_email, base_output_path, base_runfiles_path, wholecell_master_dir, affiliation = 'Genome Design Group, Bristol Centre for Complexity Science, BrisSynBio, University of Bristol.', activate_virtual_environment_list = ['module add apps/anaconda3-2.3.0', 'source activate whole_cell_modelling_suite'], path_to_flex1 = '/projects/flex1', relative_to_flex1_path_to_communual_data = 'database'):
        Bg.__init__(self, cluster_user_name, ssh_config_alias, forename_of_user, surname_of_user, user_email, base_output_path, base_runfiles_path, affiliation)
        self.db_connection = self
        self.ko_queue = 'cpu'
        self.unittest_queue = 'cpu'
        Karr2012General.__init__(self, wholecell_master_dir, activate_virtual_environment_list, path_to_flex1, relative_to_flex1_path_to_communual_data, self.db_connection)

    def createUnittestScript(self, submission_data_dict, no_file_overwrite = True):

        # unpack the dictionary
        tmp_save_path = submission_data_dict['tmp_save_path']
        name_of_job = submission_data_dict['name_of_job']
        unittest_master_dir = submission_data_dict['unittest_master_dir']
        output_dir = submission_data_dict['output_dir']
        outfiles_path = submission_data_dict['outfiles_path']
        errorfiles_path = submission_data_dict['errorfiles_path']
        no_of_unique_ko_sets = submission_data_dict['no_of_unique_ko_sets']
        no_of_repetitions_of_each_ko = submission_data_dict['no_of_repetitions_of_each_ko']
        queue_name = submission_data_dict['queue_name']
        ko_name_to_set_dict = submission_data_dict['ko_name_to_set_dict']

        submission_script_filename = tmp_save_path + '/' + name_of_job + '_submission.sh'
        # raise exception if the file already exists
        with pathlib.Path(submission_script_filename) as test_file:
            if test_file.is_file():
                raise ValueError(submission_script_filename + ' already exists!')
        
        # assign None so that we can check things worked later
        job_array_numbers = None
        # The maximum job array size on BC3
        max_job_array_size = 200
        # initialise output dict
        output_dict = {}
        # test that a reasonable amount of jobs has been submitted (This is not a hard and fast rule but there has to be a max and my intuition suggestss that it will start to get complicated around this level i.e. queueing and harddisk space etc)
        total_sims = no_of_unique_ko_sets * no_of_repetitions_of_each_ko
        if total_sims > 20000:
                raise ValueError('Total amount of simulations for one batch submission must be less than 20,000, here total_sims=',total_sims)

        output_dict['total_sims'] = total_sims
        # spread simulations across array jobs
        if no_of_unique_ko_sets <= max_job_array_size:
                no_of_unique_ko_sets_per_array_job = 1
                no_of_arrays = no_of_unique_ko_sets
                job_array_numbers = '1-' + str(no_of_unique_ko_sets)
                walltime = '00:10:00'
        else:
                # job_array_size * no_of_unique_ko_sets_per_array_job = no_of_unique_ko_sets so all the factors of no_of_unique_ko_sets is
                common_factors = [x for x in range(1, no_of_unique_ko_sets+1) if no_of_unique_ko_sets % x == 0]
                # make the job_array_size as large as possible such that it is less than max_job_array_size
                factor_idx = len(common_factors) - 1
                while factor_idx >= 0:
                        if common_factors[factor_idx] < max_job_array_size:
                                job_array_numbers = '1-' + str(common_factors[factor_idx])
                                no_of_arrays = common_factors[factor_idx]
                                no_of_unique_ko_sets_per_array_job = common_factors[(len(common_factors)-1) - factor_idx]
                                factor_idx = -1
                        else:
                                factor_idx -= 1

                # raise error if no suitable factors found!
                if job_array_numbers is None:
                        raise ValueError('job_array_numbers should have been assigned by now! This suggests that it wasn\'t possible for my algorithm to split the KOs across the job array properly. Here no_of_unique_ko_sets=', no_of_unique_ko_sets, ' and the common factors of this number are:', common_factors)

                # add some time to the walltime because I don't think the jobs have to startat the same time
                walltime = '00:10:00'

        output_dict['no_of_arrays'] = no_of_arrays
        output_dict['no_of_unique_kos_per_array_job'] = no_of_unique_ko_sets_per_array_job
        output_dict['no_of_repetitions_of_each_ko'] = no_of_repetitions_of_each_ko
        # calculate the amount of cores per array job - NOTE: for simplification we only use cores and not nodes (this is generally the fastest way to get through the queue anyway)
        no_of_cores = no_of_repetitions_of_each_ko * no_of_unique_ko_sets_per_array_job
        output_dict['no_of_sims_per_array_job'] = no_of_cores
        output_dict['list_of_rep_dir_names'] = list(range(1, no_of_repetitions_of_each_ko + 1))
        no_of_nodes = 1

        # We use the standard submission script template inherited form the Pbs class and then add the following code to the bottom of it
        #list_of_job_specific_code = self.activate_virtual_environment_list.copy()
        # split output dir into the base path and the relative path (so that it fits the form neccessary for the bash script i.e. abs to flex1 and database to destination)
        base_relativeDestination_dict = {'base_path': [], 'relative_destination_path': []}
        at_database_flag = False
        for directory in output_dir.split('/'):
            if directory != '':
                if directory == 'database':
                    at_database_flag = True

                if at_database_flag:
                    base_relativeDestination_dict['relative_destination_path'] += [directory]
                else:
                    base_relativeDestination_dict['base_path'] += [directory]

        # convert the lists of dirs back into path strings
        base_relativeDestination_dict['relative_destination_path'] = "/".join(base_relativeDestination_dict['relative_destination_path'])
        base_relativeDestination_dict['base_path'] = "/".join(base_relativeDestination_dict['base_path'])
        base_relativeDestination_dict['base_path'] = '/' + base_relativeDestination_dict['base_path']
        # create list of job specific code
        ko_names = tuple(ko_name_to_set_dict.keys())
        bash_array_creation = "ko_names=("
        for name in ko_names:
            bash_array_creation += name + " "
            
        bash_array_creation = bash_array_creation[:-1]
        bash_array_creation += ")"
        list_of_job_specific_code = [bash_array_creation + "\n", "master=" + unittest_master_dir + "\n", "# create output directory", "base_outDir=" + output_dir + "\n", "# go to master directory", "cd ${master}" + "\n", "./copy_data_from_test_data.sh " + base_relativeDestination_dict['base_path'] + ' ' + base_relativeDestination_dict['relative_destination_path'] + '/${ko_names[$((${SLURM_ARRAY_TASK_ID}-1))]}']

        # get the standard submission script
        standard_submission_script = self.createSubmissionScriptTemplate(name_of_job, no_of_nodes, no_of_cores, job_array_numbers, walltime, queue_name, outfiles_path, errorfiles_path, initial_message_in_code = self.initial_message_in_code, slurm_account_name = self.slurm_account_name, shebang = "#!/bin/bash -login\n")

        self.createStandardSubmissionScript(submission_script_filename, standard_submission_script + list_of_job_specific_code)

        output_dict['submission_script_filename'] = submission_script_filename

        return output_dict

    def createWcmKoScript(self, submission_data_dict):

        # unpack the dictionary
        tmp_save_path = submission_data_dict['tmp_save_path']
        name_of_job = submission_data_dict['name_of_job']
        wholecell_model_master_dir = submission_data_dict['wholecell_model_master_dir']
        output_dir = submission_data_dict['output_dir']
        outfiles_path = submission_data_dict['outfiles_path']
        errorfiles_path = submission_data_dict['errorfiles_path']
        path_and_name_of_ko_codes = submission_data_dict['path_and_name_of_ko_codes']
        path_and_name_of_unique_ko_dir_names = submission_data_dict['path_and_name_of_unique_ko_dir_names']
        no_of_unique_ko_sets = len(submission_data_dict['ko_name_to_set_dict'])
        no_of_repetitions_of_each_ko = submission_data_dict['no_of_repetitions_of_each_ko']
        queue_name = submission_data_dict['queue_name']

        submission_script_filename = tmp_save_path + '/' + name_of_job + '_submission.sh'
        # assign None so that we can check things worked later
        job_array_numbers = None
        # The maximum job array size on BG
        max_job_array_size = 200
        # initialise output dict
        output_dict = {}
        # test that a reasonable amount of jobs has been submitted (This is not a hard and fast rule but there has to be a max and my intuition suggestss that it will start to get complicated around this level i.e. queueing and harddisk space etc)
        total_sims = no_of_unique_ko_sets * no_of_repetitions_of_each_ko
        if total_sims > 20000:
                raise ValueError('Total amount of simulations for one batch submission must be less than 20,000, here total_sims=',total_sims)

        output_dict['total_sims'] = total_sims
        # spread simulations across array jobs
        if no_of_unique_ko_sets <= max_job_array_size:
                no_of_unique_ko_sets_per_array_job = 1
                no_of_arrays = no_of_unique_ko_sets
                job_array_numbers = '1-' + str(no_of_unique_ko_sets)
                walltime = '30:00:00'
        else:
                # job_array_size * no_of_unique_ko_sets_per_array_job = no_of_unique_ko_sets so all the factors of no_of_unique_ko_sets is
                common_factors = [x for x in range(1, no_of_unique_ko_sets+1) if no_of_unique_ko_sets % x == 0]
                # make the job_array_size as large as possible such that it is less than max_job_array_size
                factor_idx = len(common_factors) - 1
                while factor_idx >= 0:
                        if common_factors[factor_idx] < max_job_array_size:
                                job_array_numbers = '1-' + str(common_factors[factor_idx])
                                no_of_arrays = common_factors[factor_idx]
                                no_of_unique_ko_sets_per_array_job = common_factors[(len(common_factors)-1) - factor_idx]
                                factor_idx = -1
                        else:
                                factor_idx -= 1

                # raise error if no suitable factors found!
                if job_array_numbers is None:
                        raise ValueError('job_array_numbers should have been assigned by now! This suggests that it wasn\'t possible for my algorithm to split the KOs across the job array properly. Here no_of_unique_ko_sets=', no_of_unique_ko_sets, ' and the common factors of this number are:', common_factors)

                # add some time to the walltime because I don't think the jobs have to startat the same time
                walltime = '35:00:00'

        output_dict['no_of_arrays'] = no_of_arrays
        output_dict['no_of_unique_kos_per_array_job'] = no_of_unique_ko_sets_per_array_job
        output_dict['no_of_repetitions_of_each_ko'] = no_of_repetitions_of_each_ko
        # calculate the amount of cores per array job - NOTE: for simplification we only use cores and not nodes (this is generally the fastest way to get through the queue anyway)
        no_of_cores = no_of_repetitions_of_each_ko * no_of_unique_ko_sets_per_array_job
        output_dict['no_of_sims_per_array_job'] = no_of_cores
        output_dict['list_of_rep_dir_names'] = list(range(1, no_of_repetitions_of_each_ko + 1))
        no_of_nodes = 1

        # We use the standard submission script template inherited form the Pbs class and then add the following code to the bottom of it
        list_of_job_specific_code = ["# load required modules", "module load apps/matlab-r2013a", 'echo "Modules loaded:"', "module list\n", "# create the master directory variable", "master=" + wholecell_model_master_dir + "\n", "# create output directory", "base_outDir=" + output_dir + "\n", "# collect the KO combos", "ko_list=" + path_and_name_of_ko_codes, "ko_dir_names=" + path_and_name_of_unique_ko_dir_names + "\n", "# Get all the gene KOs and output folder names", 'for i in `seq 1 ' + str(no_of_unique_ko_sets_per_array_job) + '`', 'do', '    Gene[${i}]=$(awk NR==$((' + str(no_of_unique_ko_sets_per_array_job) + '*(${SLURM_ARRAY_TASK_ID}-1)+${i})) ${ko_list})', '    unique_ko_dir_name[${i}]=$(awk NR==$((' + str(no_of_unique_ko_sets_per_array_job) + '*(${SLURM_ARRAY_TASK_ID}-1)+${i})) ${ko_dir_names})', "done" + "\n", "# go to master directory", "cd ${master}" + "\n", "# NB have limited MATLAB to a single thread", 'options="-nodesktop -noFigureWindows -nosplash -singleCompThread"' + "\n", "# run 16 simulations in parallel", 'echo "Running simulations (single threaded) in parallel - let\'s start the timer!"', 'start=`date +%s`' + "\n", "# create all the directories for the diarys (the normal output will be all mixed up cause it's in parrallel!)", 'for i in `seq 1 ' + str(no_of_unique_ko_sets_per_array_job) + '`', "do", '    for j in `seq 1 ' + str(no_of_repetitions_of_each_ko) + '`', "    do", '        specific_ko="$(echo ${Gene[${i}]} | sed \'s/{//g\' | sed \'s/}//g\' | sed \"s/\'//g\" | sed \'s/\"//g\' | sed \'s/,/-/g\')/${j}"', '        mkdir -p ${base_outDir}/${unique_ko_dir_name[${i}]}/diary${j}', '        matlab ${options} -r "diary(\'${base_outDir}/${unique_ko_dir_name[${i}]}/diary${j}/diary.out\');addpath(\'${master}\');setWarnings();setPath();runSimulation(\'runner\',\'koRunner\',\'logToDisk\',true,\'outDir\',\'${base_outDir}/${unique_ko_dir_name[${i}]}/${j}\',\'jobNumber\',$((no_of_repetitions_of_each_ko*no_of_unique_ko_sets_per_array_job*(${SLURM_ARRAY_TASK_ID}-1)+no_of_unique_ko_sets_per_array_job*(${i}-1)+${j})),\'koList\',{{${Gene[${i}]}}});diary off;exit;" &', "    done", "done", "wait" + "\n", "end=`date +%s`", "runtime=$((end-start))", 'echo "$((${no_of_unique_ko_sets_per_array_job}*${no_of_repetitions_of_each_ko})) simulations took: ${runtime} seconds."']

        # get the standard submission script
        standard_submission_script = self.createSubmissionScriptTemplate(name_of_job, no_of_nodes, no_of_cores, job_array_numbers, walltime, queue_name, outfiles_path, errorfiles_path, initial_message_in_code = self.initial_message_in_code, slurm_account_name = self.slurm_account_name, shebang = "#!/bin/bash -login\n")

        self.createStandardSubmissionScript(submission_script_filename, standard_submission_script + list_of_job_specific_code)

        output_dict['submission_script_filename'] = submission_script_filename

        return output_dict

class Karr2012Bc3(Bc3, Karr2012General):
    def __init__(self, cluster_user_name, ssh_config_alias, forename_of_user, surname_of_user, user_email, base_output_path, base_runfiles_path, wholecell_master_dir, affiliation = 'Genome Design Group, Bristol Centre for Complexity Science, BrisSynBio, University of Bristol.', activate_virtual_environment_list = ['module add languages/python-anaconda-4.2-3.5', 'source activate wholecell_modelling_suite'], path_to_flex1 = '/panfs/panasas01/bluegem-flex1', relative_to_flex1_path_to_communual_data = 'database'):
        Bc3.__init__(self, cluster_user_name, ssh_config_alias, forename_of_user, surname_of_user, user_email, base_output_path, base_runfiles_path, affiliation)
        self.db_connection = self
        self.ko_queue = 'veryshort'
        self.unittest_queue = 'veryshort'
        Karr2012General.__init__(self, wholecell_master_dir, activate_virtual_environment_list, path_to_flex1, relative_to_flex1_path_to_communual_data, self.db_connection)

    def createUnittestScript(self, submission_data_dict, no_file_overwrite = True):

        # unpack the dictionary
        tmp_save_path = submission_data_dict['tmp_save_path']
        name_of_job = submission_data_dict['name_of_job']
        unittest_master_dir = submission_data_dict['unittest_master_dir']
        output_dir = submission_data_dict['output_dir']
        outfiles_path = submission_data_dict['outfiles_path']
        errorfiles_path = submission_data_dict['errorfiles_path']
        no_of_unique_ko_sets = submission_data_dict['no_of_unique_ko_sets']
        no_of_repetitions_of_each_ko = submission_data_dict['no_of_repetitions_of_each_ko']
        queue_name = submission_data_dict['queue_name']
        ko_name_to_set_dict = submission_data_dict['ko_name_to_set_dict']

        submission_script_filename = tmp_save_path + '/' + name_of_job + '_submission.sh'
        # raise exception if the file already exists
        with pathlib.Path(submission_script_filename) as test_file:
            if test_file.is_file():
                raise ValueError(submission_script_filename + ' already exists!')
        
        # assign None so that we can check things worked later
        job_array_numbers = None
        # The maximum job array size on BC3
        max_job_array_size = 500
        # initialise output dict
        output_dict = {}
        # test that a reasonable amount of jobs has been submitted (This is not a hard and fast rule but there has to be a max and my intuition suggestss that it will start to get complicated around this level i.e. queueing and harddisk space etc)
        total_sims = no_of_unique_ko_sets * no_of_repetitions_of_each_ko
        if total_sims > 20000:
                raise ValueError('Total amount of simulations for one batch submission must be less than 20,000, here total_sims=',total_sims)

        output_dict['total_sims'] = total_sims
        # spread simulations across array jobs
        if no_of_unique_ko_sets <= max_job_array_size:
                no_of_unique_ko_sets_per_array_job = 1
                no_of_arrays = no_of_unique_ko_sets
                job_array_numbers = '1-' + str(no_of_unique_ko_sets)
                walltime = '00:10:00'
        else:
                # job_array_size * no_of_unique_ko_sets_per_array_job = no_of_unique_ko_sets so all the factors of no_of_unique_ko_sets is
                common_factors = [x for x in range(1, no_of_unique_ko_sets+1) if no_of_unique_ko_sets % x == 0]
                # make the job_array_size as large as possible such that it is less than max_job_array_size
                factor_idx = len(common_factors) - 1
                while factor_idx >= 0:
                        if common_factors[factor_idx] < max_job_array_size:
                                job_array_numbers = '1-' + str(common_factors[factor_idx])
                                no_of_arrays = common_factors[factor_idx]
                                no_of_unique_ko_sets_per_array_job = common_factors[(len(common_factors)-1) - factor_idx]
                                factor_idx = -1
                        else:
                                factor_idx -= 1

                # raise error if no suitable factors found!
                if job_array_numbers is None:
                        raise ValueError('job_array_numbers should have been assigned by now! This suggests that it wasn\'t possible for my algorithm to split the KOs across the job array properly. Here no_of_unique_ko_sets=', no_of_unique_ko_sets, ' and the common factors of this number are:', common_factors)

                # add some time to the walltime because I don't think the jobs have to startat the same time
                walltime = '00:10:00'

        output_dict['no_of_arrays'] = no_of_arrays
        output_dict['no_of_unique_kos_per_array_job'] = no_of_unique_ko_sets_per_array_job
        output_dict['no_of_repetitions_of_each_ko'] = no_of_repetitions_of_each_ko
        # calculate the amount of cores per array job - NOTE: for simplification we only use cores and not nodes (this is generally the fastest way to get through the queue anyway)
        no_of_cores = no_of_repetitions_of_each_ko * no_of_unique_ko_sets_per_array_job
        output_dict['no_of_sims_per_array_job'] = no_of_cores
        output_dict['list_of_rep_dir_names'] = list(range(1, no_of_repetitions_of_each_ko + 1))
        no_of_nodes = 1

        # We use the standard submission script template inherited form the Pbs class and then add the following code to the bottom of it
        #list_of_job_specific_code = self.activate_virtual_environment_list.copy()
        # split output dir into the base path and the relative path (so that it fits the form neccessary for the bash script i.e. abs to flex1 and database to destination)
        base_relativeDestination_dict = {'base_path': [], 'relative_destination_path': []}
        at_database_flag = False
        for directory in output_dir.split('/'):
            if directory != '':
                if directory == 'database':
                    at_database_flag = True

                if at_database_flag:
                    base_relativeDestination_dict['relative_destination_path'] += [directory]
                else:
                    base_relativeDestination_dict['base_path'] += [directory]

        # convert the lists of dirs back into path strings
        base_relativeDestination_dict['relative_destination_path'] = "/".join(base_relativeDestination_dict['relative_destination_path'])
        base_relativeDestination_dict['base_path'] = "/".join(base_relativeDestination_dict['base_path'])
        base_relativeDestination_dict['base_path'] = '/' + base_relativeDestination_dict['base_path']
        # create list of job specific code
        ko_names = tuple(ko_name_to_set_dict.keys())
        bash_array_creation = "ko_names=("
        for name in ko_names:
            bash_array_creation += name + " "
            
        bash_array_creation = bash_array_creation[:-1]
        bash_array_creation += ")"
        list_of_job_specific_code = [bash_array_creation + "\n", "master=" + unittest_master_dir + "\n", "# create output directory", "base_outDir=" + output_dir + "\n", "# go to master directory", "cd ${master}" + "\n", "copy_data_from_test_data.sh " + base_relativeDestination_dict['base_path'] + ' ' + base_relativeDestination_dict['relative_destination_path'] + '/${ko_names[$((${PBS_ARRAYID}-1))]}']

        # get the standard submission script
        standard_submission_script = self.createSubmissionScriptTemplate(name_of_job, no_of_nodes, no_of_cores, job_array_numbers, walltime, queue_name, outfiles_path, errorfiles_path, initial_message_in_code = self.initial_message_in_code)

        self.createStandardSubmissionScript(submission_script_filename, standard_submission_script + list_of_job_specific_code)

        output_dict['submission_script_filename'] = submission_script_filename

        return output_dict

    def createWcmKoScript(self, submission_data_dict):

        # unpack the dictionary
        tmp_save_path = submission_data_dict['tmp_save_path']
        name_of_job = submission_data_dict['name_of_job']
        wholecell_model_master_dir = submission_data_dict['wholecell_model_master_dir']
        output_dir = submission_data_dict['output_dir']
        outfiles_path = submission_data_dict['outfiles_path']
        errorfiles_path = submission_data_dict['errorfiles_path']
        path_and_name_of_ko_codes = submission_data_dict['path_and_name_of_ko_codes']
        path_and_name_of_unique_ko_dir_names = submission_data_dict['path_and_name_of_unique_ko_dir_names']
        no_of_unique_ko_sets = len(submission_data_dict['ko_name_to_set_dict'])
        no_of_repetitions_of_each_ko = submission_data_dict['no_of_repetitions_of_each_ko']
        queue_name = submission_data_dict['queue_name']

        submission_script_filename = tmp_save_path + '/' + name_of_job + '_submission.sh'
        # assign None so that we can check things worked later
        job_array_numbers = None
        # The maximum job array size on BC3
        max_job_array_size = 500
        # initialise output dict
        output_dict = {}
        # test that a reasonable amount of jobs has been submitted (This is not a hard and fast rule but there has to be a max and my intuition suggestss that it will start to get complicated around this level i.e. queueing and harddisk space etc)
        total_sims = no_of_unique_ko_sets * no_of_repetitions_of_each_ko
        if total_sims > 20000:
                raise ValueError('Total amount of simulations for one batch submission must be less than 20,000, here total_sims=',total_sims)

        output_dict['total_sims'] = total_sims
        # spread simulations across array jobs
        if no_of_unique_ko_sets <= max_job_array_size:
                no_of_unique_ko_sets_per_array_job = 1
                no_of_arrays = no_of_unique_ko_sets
                job_array_numbers = '1-' + str(no_of_unique_ko_sets)
                walltime = '30:00:00'
        else:
                # job_array_size * no_of_unique_ko_sets_per_array_job = no_of_unique_ko_sets so all the factors of no_of_unique_ko_sets is
                common_factors = [x for x in range(1, no_of_unique_ko_sets+1) if no_of_unique_ko_sets % x == 0]
                # make the job_array_size as large as possible such that it is less than max_job_array_size
                factor_idx = len(common_factors) - 1
                while factor_idx >= 0:
                        if common_factors[factor_idx] < max_job_array_size:
                                job_array_numbers = '1-' + str(common_factors[factor_idx])
                                no_of_arrays = common_factors[factor_idx]
                                no_of_unique_ko_sets_per_array_job = common_factors[(len(common_factors)-1) - factor_idx]
                                factor_idx = -1
                        else:
                                factor_idx -= 1

                # raise error if no suitable factors found!
                if job_array_numbers is None:
                        raise ValueError('job_array_numbers should have been assigned by now! This suggests that it wasn\'t possible for my algorithm to split the KOs across the job array properly. Here no_of_unique_ko_sets=', no_of_unique_ko_sets, ' and the common factors of this number are:', common_factors)

                # add some time to the walltime because I don't think the jobs have to startat the same time
                walltime = '35:00:00'

        output_dict['no_of_arrays'] = no_of_arrays
        output_dict['no_of_unique_kos_per_array_job'] = no_of_unique_ko_sets_per_array_job
        output_dict['no_of_repetitions_of_each_ko'] = no_of_repetitions_of_each_ko
        # calculate the amount of cores per array job - NOTE: for simplification we only use cores and not nodes (this is generally the fastest way to get through the queue anyway)
        no_of_cores = no_of_repetitions_of_each_ko * no_of_unique_ko_sets_per_array_job
        output_dict['no_of_sims_per_array_job'] = no_of_cores
        output_dict['list_of_rep_dir_names'] = list(range(1, no_of_repetitions_of_each_ko + 1))
        no_of_nodes = 1

        # We use the standard submission script template inherited form the Pbs class and then add the following code to the bottom of it
        list_of_job_specific_code = ["# load required modules", "module load apps/matlab-r2013a", 'echo "Modules loaded:"', "module list\n", "# create the master directory variable", "master=" + wholecell_model_master_dir + "\n", "# create output directory", "base_outDir=" + output_dir + "\n", "# collect the KO combos", "ko_list=" + path_and_name_of_ko_codes, "ko_dir_names=" + path_and_name_of_unique_ko_dir_names + "\n", "# Get all the gene KOs and output folder names", 'for i in `seq 1 ' + str(no_of_unique_ko_sets_per_array_job) + '`', 'do', '    Gene[${i}]=$(awk NR==$((' + str(no_of_unique_ko_sets_per_array_job) + '*(${PBS_ARRAYID}-1)+${i})) ${ko_list})', '    unique_ko_dir_name[${i}]=$(awk NR==$((' + str(no_of_unique_ko_sets_per_array_job) + '*(${PBS_ARRAYID}-1)+${i})) ${ko_dir_names})', "done" + "\n", "# go to master directory", "cd ${master}" + "\n", "# NB have limited MATLAB to a single thread", 'options="-nodesktop -noFigureWindows -nosplash -singleCompThread"' + "\n", "# run 16 simulations in parallel", 'echo "Running simulations (single threaded) in parallel - let\'s start the timer!"', 'start=`date +%s`' + "\n", "# create all the directories for the diarys (the normal output will be all mixed up cause it's in parrallel!)", 'for i in `seq 1 ' + str(no_of_unique_ko_sets_per_array_job) + '`', "do", '    for j in `seq 1 ' + str(no_of_repetitions_of_each_ko) + '`', "    do", '        specific_ko="$(echo ${Gene[${i}]} | sed \'s/{//g\' | sed \'s/}//g\' | sed \"s/\'//g\" | sed \'s/\"//g\' | sed \'s/,/-/g\')/${j}"', '        mkdir -p ${base_outDir}/${unique_ko_dir_name[${i}]}/diary${j}', '        matlab ${options} -r "diary(\'${base_outDir}/${unique_ko_dir_name[${i}]}/diary${j}/diary.out\');addpath(\'${master}\');setWarnings();setPath();runSimulation(\'runner\',\'koRunner\',\'logToDisk\',true,\'outDir\',\'${base_outDir}/${unique_ko_dir_name[${i}]}/${j}\',\'jobNumber\',$((no_of_repetitions_of_each_ko*no_of_unique_ko_sets_per_array_job*(${PBS_ARRAYID}-1)+no_of_unique_ko_sets_per_array_job*(${i}-1)+${j})),\'koList\',{{${Gene[${i}]}}});diary off;exit;" &', "    done", "done", "wait" + "\n", "end=`date +%s`", "runtime=$((end-start))", 'echo "$((${no_of_unique_ko_sets_per_array_job}*${no_of_repetitions_of_each_ko})) simulations took: ${runtime} seconds."']

        # get the standard submission script
        standard_submission_script = self.createSubmissionScriptTemplate(name_of_job, no_of_nodes, no_of_cores, job_array_numbers, walltime, queue_name, outfiles_path, errorfiles_path, initial_message_in_code = self.initial_message_in_code)

        self.createStandardSubmissionScript(submission_script_filename, standard_submission_script + list_of_job_specific_code)

        output_dict['submission_script_filename'] = submission_script_filename

        return output_dict

