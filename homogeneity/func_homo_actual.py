import os
import numpy as np
import pandas as pd
import glob
import nibabel as nib

def compute_parcel_homogeneity(parcel_time_series):
    """
    Compute the homogeneity for a single parcel based on its time series.
    """
    # Compute pairwise Pearson correlations across the t-values
    correlations = np.corrcoef(parcel_time_series, rowvar=False)
    
    # Clip correlation values to avoid -inf and inf in arctanh
    correlations = np.clip(correlations, -0.999999, 0.999999)
    
    # Apply Fisher z-transformation
    correlations = np.arctanh(correlations)
    
    # Calculate the average correlation excluding diagonal
    upper_triangle_indices = np.triu_indices_from(correlations, k=1)
    avg_correlation = np.nanmean(correlations[upper_triangle_indices])
    
    return avg_correlation

def process_group_data(parcel_csv_dir, num_parcels=36):
    """
    Compute the homogeneity for each parcel and then compute the weighted average homogeneity across all parcels.
    """
    parcel_homogeneities = {}
    parcel_sizes = {}

    for parcel_id in range(1, num_parcels+1):
        parcel_file = os.path.join(parcel_csv_dir, f'parcel_{parcel_id}_2d.csv')
        if os.path.exists(parcel_file):
            print(f"Processing {parcel_file}...")
            try:
                # Read the time series data from CSV, assuming the first row is a header
                parcel_time_series = pd.read_csv(parcel_file, header=0).values
                
                # Compute homogeneity for the current parcel
                homogeneity = compute_parcel_homogeneity(parcel_time_series)
                parcel_homogeneities[parcel_id] = homogeneity
                
                # Store the number of voxels in the current parcel
                parcel_sizes[parcel_id] = parcel_time_series.shape[1]
            except Exception as e:
                print(f"Failed to process {parcel_file}: {e}")
        else:
            print(f"Parcel file {parcel_file} not found.")

    # Compute the weighted average homogeneity across all parcels
    weighted_homogeneity_sum = sum(parcel_homogeneities[parcel_id] * parcel_sizes[parcel_id] for parcel_id in parcel_homogeneities)
    total_voxel_count = sum(parcel_sizes.values())

    if total_voxel_count > 0:
        group_average_homogeneity = weighted_homogeneity_sum / total_voxel_count
    else:
        group_average_homogeneity = 0  # Handle the edge case where voxel count is zero

    # Save the parcel homogeneities and sizes to a CSV file
    output_csv = os.path.join(parcel_csv_dir, 'parcel_homogeneities.csv')
    homogeneity_df = pd.DataFrame.from_dict(parcel_homogeneities, orient='index', columns=['Homogeneity'])
    homogeneity_df['ParcelSize'] = pd.Series(parcel_sizes)
    homogeneity_df.to_csv(output_csv)
    print(f"Saved parcel homogeneities to {output_csv}")

    return group_average_homogeneity

# Run
parcel_csv_dir = 'parcel_csv_files'  # Directory containing the CSV files for each parcel

# Compute and output the group-level homogeneity metric
group_average_homogeneity = process_group_data(parcel_csv_dir)
print(f"Group average homogeneity: {group_average_homogeneity}")


