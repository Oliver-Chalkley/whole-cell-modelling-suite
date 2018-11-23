# Author: Oliver Chalkley
# Affiliation: Bristol Centre for Complexity Science (BCCS) and the Bristol Genome Design Group (GDG)
# Date of creation: 06/12/2017

# import libraries
import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import sklearn
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.cluster import adjusted_rand_score
from sklearn.decomposition import PCA
import dill
from tqdm import tqdm
from multiprocessing import Pool, current_process
import multiprocessing

class Genes():
    def __init__(self, db_conn, all_gene_codes_list, genome_data = None, data_input_type = 'genome'):
        self.db_conn = db_conn
        if all_gene_codes_list is None:
            self.all_gene_codes_list = self.db_conn.getJr358Genes()
        else:
            self.all_gene_codes_list = all_gene_codes_list
        self.ko_code_to_id_dict = self.db_conn.convertGeneCodeToId(self.all_gene_codes_list)
        self.ko_id_to_code_dict = self.invertDictionary(self.ko_code_to_id_dict)
        # make sure the genes list is in order (visualisations need to be universally consistent!!)
        ordered_ids = sorted(list(self.ko_id_to_code_dict.keys()))
        self.all_gene_codes_list = [self.ko_id_to_code_dict[ids] for ids in ordered_ids]
        self.idx_to_id_dict = self.createIdxToIdDict(self.ko_code_to_id_dict)
        self.id_to_idx_dict = self.invertDictionary(self.idx_to_id_dict)
        if genome_data is None:
            self.genomes = pd.DataFrame(index=self.all_gene_codes_list)
        elif data_input_type == 'genome':
            self.genomes = genome_data.copy()
        elif data_input_type == 'name_to_ko_code_dict':
            name_to_ko_code_dict = genome_data.copy()
            self.genomes = self.convertKoDictToGenomes(self.name_to_ko_code_dict)
        elif data_input_type == 'name_to_ko_id_dict':
            name_to_ko_id_dict = genome_data.copy()
            self.genomes = self.convertKoDictToGenomes(self.convertKoIdDictToCodes(name_to_ko_id_dict))
        elif data_input_type == 'dataframe':
            self.genomes = genome_data.copy()
        else:
            raise ValueError('data_input_type can only be \'genome\' or \'name_to_ko_code_dict\' but here data_input_type = ', data_input_type)

### DISTANCE MATRACIES/FUNCTIONS

    @staticmethod
    def percentageSimilarityDistance(genome1, genome2):
        if len(genome1) != len(genome2):
            raise ValueError('Genome1 and genome2 must have the same length!')

        is_gene_correct = [1 if genome1[idx] == genome2[idx] else 0 for idx in range(len(genome1))]

        return (1 - sum(is_gene_correct)/(len(is_gene_correct) * 1.0))

    @staticmethod
    def percentageKIsDistance(genome1, genome2):
        if len(genome1) != len(genome2):
            raise ValueError('Genome1 and genome2 must have the same length!')


    @staticmethod
    def percentageKOsDistance(genome1, genome2):
        if len(genome1) != len(genome2):
            raise ValueError('Genome1 and genome2 must have the same length!')

    @staticmethod
    def ariDistance(genome1, genome2):
        """Takes a dictionary of KO sets and returns a distance (or similarity) matrix which is basically how many genes do they have in common."""
        if len(genome1) != len(genome2):
            raise ValueError('Genome1 and genome2 must have the same length!')

        return (1 - adjusted_rand_score(genome1, genome2))

    def createDistanceMatrix(self, distance_function, child_process_chunksize = 15, number_of_cores = None):
        """Takes a dictionary of KO sets and returns a distance (or similarity) matrix which is basically how many genes do they have in common."""
        if number_of_cores is None:
            number_of_cores = multiprocessing.cpu_count()
        print('Creating distance matrix using ', number_of_cores, 'cores.')
        genomes_df = self.genomes.copy()
        no_of_genes, no_of_genomes = genomes_df.shape
        list_of_genome_names = list(genomes_df.columns)
        list_of_genomes = [list(genomes_df.loc[:, name]) for name in list_of_genome_names]
        distance_matrix = []
        for genome in tqdm(list_of_genomes):
            with Pool(processes = number_of_cores) as pool:
                    fut = pool.starmap_async(distance_function, zip([genome] * len(list_of_genomes), list_of_genomes), chunksize = child_process_chunksize)
                    fut.wait()
            distance_matrix.append(fut.get())
#        distance_matrix = [[distance_function(list_of_genomes[i], list_of_genomes[j]) for j in range(no_of_genomes)] for i in range(no_of_genomes)]
        distance_matrix = pd.DataFrame(distance_matrix, columns = list_of_genomes, index = list_of_genomes)


        return distance_matrix

### DISTANCE FUNCTIONS/VISUALISATIONS

    def plotDistanceMatrixWithPca(self, distance_matrix, create_plot = True, show_now = True, title = None, save_figure_name = None, final_df_filename = None, genome_names_list = None, genome_class_labels_list = None, standardise_data = True, desired_dimensions = 2, xlabel_name = 'Principal Component 1', ylabel_name = 'Principal Component 2'):
        distance_matrix = distance_matrix.copy()
        if standardise_data == True:
            distance_matrix = StandardScaler().fit_transform(distance_matrix)

        pca = PCA(n_components = desired_dimensions)
        principalComponents = pca.fit_transform(distance_matrix)
        principalDf = pd.DataFrame(data = principalComponents, columns = ['principal component 1', 'principal component 2'])
        if genome_names_list is not None:
            genome_names = pd.Series(genome_names_list)
            genome_names.name = 'name'
            finalDf1 = pd.concat([principalDf, genome_names], axis = 1)
        else:
            genome_names = pd.Series(['no_names'] * len(principalDf))
            genome_names.name = 'name'
            finalDf1 = pd.concat([principalDf, genome_names], axis = 1)
        if genome_class_labels_list is not None:
            class_labels = pd.Series(genome_class_labels_list)
            class_labels.name = 'target'
            finalDf = pd.concat([finalDf1, class_labels], axis = 1)
        else:
            class_labels = pd.Series(['no_classes'] * len(principalDf))
            class_labels.name = 'target'
            finalDf = pd.concat([finalDf1, class_labels], axis = 1)

        if final_df_filename is not None:
            finalDf.to_pickle(final_df_filename)

        if create_plot == True:
            fig = plt.figure()
            ax = fig.add_subplot(1,1,1)
            
            ax.set_xlabel(xlabel_name)
            ax.set_ylabel(ylabel_name)
            if title is not None:
                ax.set_title(title)
    
            ax.scatter(finalDf.loc[:, 'principal component 1'], finalDf.loc[:, 'principal component 2'])
    
            if save_figure_name is not None:
                plt.savefig(save_figure_name, bbox_inches='tight')
            if show_now == True:
                plt.show()

        return

    def orderGeneomesWithDbscan(self, genomes, distance_matrix):
        # calculate the average distance for DBSCAN
        genomes = genomes.copy()
        distance_matrix = distance_matrix.copy()
        average_distance = distance_matrix.mean()
        min_group_size = 1
        db = DBSCAN(eps = average_distance, min_samples = min_group_size, metric="precomputed")
        db.fit_predict(distance_matrix)
        clust_groups = db.labels_
        max_group = max(clust_groups)

        # create empty array for reordered genomes
        genomes_reordered = np.empty(genomes.shape)
        genomes_reordered[:] = np.NAN
        counter = 0
        for group in range(max_group + 1):
            group_idxs = [i for i, j in enumerate(clust_groups) if j == group]
            for idx in group_idxs:
                genomes_reordered[counter, :] = genomes[idx, :]
                counter += 1

        return genomes_reordered

    def plotDendogramOfMGSs(self, distance_matrix, filename = None, legend_labels = None):
        dist_matrix_condensed = hc.distance.squareform(distance_matrix)
        z = hc.linkage(dist_matrix_condensed, method='average')
        dendrogram = hc.dendrogram(z)
        if legend_labels is not None:
            plt.legend(legend_labels)

        if filename is None:
            plt.show()
        else:
            plt.savefig(filename, bbox_inches='tight')

        return 

### KO/KI SUMMARIES

    def plotDistributionOfGeneEssentiality(self):
        ko_percentages = self.genomes.sum(axis=1)/len(self.genomes.columns)
        ko_percentages.plot(kind='hist')
        plt.show()

        return

    def summeriseEssentialityByGene(self):
        """This function compares all the genomes in the instance and categorises each gene as universally essential, universally non-essential or transient."""
        # find out the amount and size of genomes we're dealing with
        size_of_genome, no_of_genomes = self.genomes.shape
        # get gene codes for universally non-essential genes
        universal_ne_codes_tuple = tuple(self.genomes.index[(self.genomes.sum(axis=1) == 0)])
        # get gene codes for universally essential genes
        universal_e_codes_tuple = tuple(self.genomes.index[(self.genomes.sum(axis=1) == no_of_genomes)])
        # get gene codes for universally essential genes
        transient_codes_tuple = tuple(self.genomes.index[( (self.genomes.sum(axis=1) > 0) & (self.genomes.sum(axis=1) < no_of_genomes) )])

        # create output dict
        output_dict = {'universal_essential_codes': universal_e_codes_tuple, 'universal_non_essential_codes': universal_ne_codes_tuple, 'transient_codes': transient_codes_tuple}

        return output_dict

    def getGeneCodesBySimilarityClassification(self, genome1, genome2, name_of_genome1, name_of_genome2):
        """This function takes two genomes and returns a dictionary of classification to gene codes where the classifications are agreed KIs, agreed KOs, genome1/2 specific KIs, and genome1/2 specific KOs."""
        agreed_ki_idx = tuple([idx for idx in range(len(genome1)) if (genome1[idx] == genome2[idx] and genome1[idx] == 1)])
        agreed_ko_idx = tuple([idx for idx in range(len(genome1)) if (genome1[idx] == genome2[idx] and genome1[idx] == 0)])
        genome1_ki_idx = tuple([idx for idx in range(len(genome1)) if (genome1[idx] != genome2[idx] and genome1[idx] == 1)])
        genome2_ki_idx = tuple([idx for idx in range(len(genome1)) if (genome1[idx] != genome2[idx] and genome2[idx] == 1)])
        genome1_ko_idx = tuple([idx for idx in range(len(genome1)) if (genome1[idx] != genome2[idx] and genome1[idx] == 0)])
        genome2_ko_idx = tuple([idx for idx in range(len(genome1)) if (genome1[idx] != genome2[idx] and genome2[idx] == 0)])
        # convert into codes and put into a dict
        names = ('agreed_kis', 'agreed_kos', name_of_genome1 + '_kis', name_of_genome2 + '_kis', name_of_genome1 + '_kos', name_of_genome2 + '_kos')
        output_dict = {'agreed_kis': tuple([self.ko_id_to_code_dict[self.idx_to_id_dict[idx]] for idx in agreed_ki_idx]), 'agreed_kos': tuple([self.ko_id_to_code_dict[self.idx_to_id_dict[idx]] for idx in agreed_ko_idx]), name_of_genome1 + '_specific_kis': tuple([self.ko_id_to_code_dict[self.idx_to_id_dict[idx]] for idx in genome1_ki_idx]), name_of_genome2 + '_specific_kis': tuple([self.ko_id_to_code_dict[self.idx_to_id_dict[idx]] for idx in genome2_ki_idx]), name_of_genome1 + '_specific_kos': tuple([self.ko_id_to_code_dict[self.idx_to_id_dict[idx]] for idx in genome1_ko_idx]), name_of_genome2 + '_specific_kos': tuple([self.ko_id_to_code_dict[self.idx_to_id_dict[idx]] for idx in genome2_ko_idx])}

        return output_dict

#### CONVERTING BETWEEN DATA REPRESENTATIONS

    def invertDictionary(self, input_dict):
        """This function takes a dictionary and inverts it (assuming it's one to one)."""
        inverse_dict = {v: k for k, v in input_dict.items()}

        return inverse_dict

    def createIdxToIdDict(self, code_to_id_dict):
        list_of_ids = list(code_to_id_dict.values())
        # sort them into ascending order (just because the order of dicts aren't alwayys preserved and so provided we are using the same JR genes to start with we can compare the indexs provided they are ordered in ascending order) maybe not neccessary but avoiding hard to find bug later on
        list_of_ids.sort()
        idx_to_id_dict = {idx: list_of_ids[idx] for idx in range(len(list_of_ids))}

        return idx_to_id_dict

    def convertKoIdDictToCodes(self, name_to_ko_set_ids_dict):
        name_to_ko_set_codes_dict = {ko_set_name: tuple([self.ko_id_to_code_dict[ko_id] for ko_id in name_to_ko_set_ids_dict[ko_set_name]]) for ko_set_name in name_to_ko_set_ids_dict.keys()}

        return name_to_ko_set_codes_dict

    def convertKoDictToGenomes(self, name_to_ko_set_codes_dict):
        no_of_genes = len(self.ko_code_to_id_dict)
        ko_sets = name_to_ko_set_codes_dict.copy()

        wt_genome = [1]*no_of_genes
        genomes = [float('NaN') for i in range(len(ko_sets))]
        idx_to_id_dict = self.idx_to_id_dict.copy()
        id_to_idx_dict = self.id_to_idx_dict.copy()
        ko_set_names = list(ko_sets.keys())
        for ko_set_idx in range(len(ko_sets)):
            tmp_genome = wt_genome.copy()
            for gene_code in ko_sets[ko_set_names[ko_set_idx]]:
                ids = self.ko_code_to_id_dict[gene_code]
                idx = id_to_idx_dict[ids]
                tmp_genome[idx] = 0

            genomes[ko_set_idx] = tmp_genome

        genomes = np.array(genomes)
        genomes = np.transpose(genomes)
        genomes = pd.DataFrame(genomes, columns=ko_set_names, index=self.all_gene_codes_list)

        return genomes

### STANDARD OPERATIONS

    def appendGenomeFromDb(self, db_filename, sql_query):
        conn = sqlite3.connect(db_filename) 
        raw_genomes = pd.read_sql(sql_query, conn)
        genome_df = self.convertRawGenomeToDf(raw_genomes)
        self.appendGenomeDf(genome_df)

    def appendGenomeFromTxtFile(self, filename):
        raw_genomes = pd.read_csv(filename, names = ['genome'])
        genome_df = self.convertRawGenomeToDf(raw_genomes)
        self.appendGenomeDf(genome_df)

    def convertRawGenomeToDf(self, raw_genomes, genome_names = None):
        all_gene_codes = self.all_gene_codes_list.copy()
        if genome_names is None:
            genome_names = ['genome' + str(idx + 1) for idx in range(len(raw_genomes.index))]

        genome_dict = {genome_names[genome_idx]: [int(gene) for gene in list(raw_genomes.iloc[genome_idx, 0])] for genome_idx in range(len(raw_genomes.index))}
        genome_df = pd.DataFrame(genome_dict, index = all_gene_codes)

        return genome_df

    def appendGenomeDf(self, genome_df):
        if (self.genomes.index != genome_df.index).all():
            raise ValueError('Cannot append different different genomes and here the indexes of both data frames don\'t match suggesting that they are different organisms.')

        self.genomes = self.genomes.join(genome_df)

        return

    def appendNameToKoIdSetDict(self, name_to_ko_id_dict):
        name_to_ko_code_dict = self.convertKoIdDictToCodes(name_to_ko_id_dict)

        self.appendNameToKoSetDict(name_to_ko_code_dict)

        return

    def appendNameToKoSetDict(self, name_to_ko_code_dict):

        self.appendGenomeDf(self.convertKoDictToGenomes(name_to_ko_code_dict))

        return
