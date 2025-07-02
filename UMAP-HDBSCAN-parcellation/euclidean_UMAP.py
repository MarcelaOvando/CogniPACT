import numpy as np
from scipy.spatial import distance
from scipy.stats import pearsonr
import pandas as pd

def calculate_distance_matrix(umap_matrix):
    """
    Calculate the Euclidean distance matrix between all points in the UMAP.
    """
    return distance.cdist(umap_matrix, umap_matrix, 'euclidean')

def calculate_pearson_correlation(matrix1, matrix2):
    """
    Calculate the Pearson correlation coefficient between two distance matrices.
    """
    flattened_matrix1 = matrix1.flatten()
    flattened_matrix2 = matrix2.flatten()

    return pearsonr(flattened_matrix1, flattened_matrix2)[0]

# Path definition (this is for association parcellation)
# These are the paths for the UMAP embedding components for the different groups
file_pathG1 = '/data/extra/movando/umap/euclidean/files_asso/umapG1_all_combined_loopFinal_noCerebellum4.csv'
file_pathG2 = '/data/extra/movando/umap/euclidean/files_asso/umapG2_all_combined_loopFinal_noCerebellum4.csv'
file_random = '/data/extra/movando/umap/euclidean/files_asso/umapRandom_all_combined_loopFinal_noCerebellum1.csv'

# Define the number of random points to sample
num_random_points = 1000


# Load data
umap_matrix_group1 = pd.read_csv(file_pathG1, header=None).sample(n=num_random_points, random_state=42)  # UMAP matrix for group 1
umap_matrix_group2 = pd.read_csv(file_pathG2, header=None).sample(n=num_random_points, random_state=42)  # UMAP matrix for group 2
umap_matrix_random = pd.read_csv(file_random, header=None).sample(n=num_random_points, random_state=42)  # UMAP matrix for random


# Calculate Euclidean distance matrices
distance_matrix_group1 = calculate_distance_matrix(umap_matrix_group1)
distance_matrix_group2 = calculate_distance_matrix(umap_matrix_group2)
distance_matrix_random = calculate_distance_matrix(umap_matrix_random)


# Save the combined array to a CSV file
np.savetxt("/data/extra/movando/umap/euclidean/files_asso/Random1000euclideanG1_final.csv", distance_matrix_group1, delimiter=",")
np.savetxt("/data/extra/movando/umap/euclidean/files_asso/Random1000euclideanG2_final.csv", distance_matrix_group2, delimiter=",")
np.savetxt("/data/extra/movando/umap/euclidean/files_asso/Random1000euclideanRandom_final.csv", distance_matrix_random, delimiter=",")

# Calculate Pearson correlation between the distance matrices
correlation_coefficientG1_G2 = calculate_pearson_correlation(distance_matrix_group1, distance_matrix_group2)
correlation_coefficientG1_random = calculate_pearson_correlation(distance_matrix_group1, distance_matrix_random)
correlation_coefficientG2_random = calculate_pearson_correlation(distance_matrix_group2, distance_matrix_random)

print(f"Pearson correlation coefficientG1-G2: {correlation_coefficientG1_G2}")
print(f"Pearson correlation coefficientG1-R: {correlation_coefficientG1_random}")
print(f"Pearson correlation coefficientG2-R: {correlation_coefficientG2_random}")



