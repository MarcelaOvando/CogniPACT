import numpy as np
import pandas as pd
import hdbscan
import hdbscan
import os
import glob
import numpy as np
import sys
import pandas as pd
from pandas import DataFrame
import nibabel as nib
import umap.umap_ as UMAP

import matplotlib.pyplot as plt
#matplotlib inline
import seaborn as sns

#from umap_outils import plot_clusters_umap

# Path to the file with the UMAP embedding components (this is an example for the association parcellation)
file_path = '/data/extra/movando/umap/umap_all_participants/all_ttest_101/asso/umap_all_combined_101part.csv'

# Read the CSV file into a DataFrame
X_embedded = pd.read_csv(file_path, header=None)

# Display the DataFrame
print(X_embedded)

print(X_embedded.shape)
x_axes = X_embedded.iloc[:, 0]
y_axes = X_embedded.iloc[:, 1]


# Define the range of parameter values
min_cluster_range = range(50, 501, 50)
min_samples_range = range(50, 501, 50)

# Create lists to store results
results = []

# Loop over parameter values
for min_cluster_size in min_cluster_range:
    for min_samples in min_samples_range:
        np.random.seed(42)
        # Fit the HDBSCAN model with the current parameter values
        clustered_data = hdbscan.hdbscan_.HDBSCAN(min_cluster_size=min_cluster_size, 
                                                   min_samples=min_samples, 
                                                   gen_min_span_tree=True).fit(X_embedded)
        # Get the labels from the clustering
        labels = clustered_data.labels_

        # Calculate the DBCV score
        dbcv_score = clustered_data.relative_validity_
        
        # Calculate coverage
        clustered = (labels >= 0)
        coverage = np.sum(clustered) / X_embedded.shape[0]
        
        # Calculate total clusters
        total_clusters = np.max(labels)

        print(f'Running min_cluster = {min_cluster_size} and min_samples = {min_samples}')
        
        # Append results to the list
        results.append({'min_cluster_size': min_cluster_size,
                        'min_samples': min_samples,
                        'dbcv_score': dbcv_score,
                        'coverage': coverage,
                        'total_clusters': total_clusters})

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Save results to CSV
results_df.to_csv('hdbscan_results_asso_101interval.csv', index=False)

