# This is to create the random parcellations and calculate their homogeneity

import os
import numpy as np
import pandas as pd
import nibabel as nib
from scipy.ndimage import label, generate_binary_structure
from sklearn.utils import shuffle
import glob

def compute_parcel_homogeneity(parcel_time_series):
    """
    Compute both the Fisher Z-transformed homogeneity and the raw correlation homogeneity
    for a single parcel based on its time series.
    """
    if parcel_time_series.shape[1] < 2:
        return np.nan, np.nan  # Return nan for both metrics if invalid

    # Compute the correlation matrix
    correlations = np.corrcoef(parcel_time_series, rowvar=False)
    correlations = np.clip(correlations, -0.999999, 0.999999)

    # Fisher Z-transformed homogeneity
    correlations_z = np.arctanh(correlations)
    upper_triangle_indices = np.triu_indices_from(correlations_z, k=1)
    avg_correlation_z = np.nanmean(correlations_z[upper_triangle_indices])

    # Raw correlation homogeneity
    avg_correlation_raw = np.nanmean(correlations[upper_triangle_indices])

    return avg_correlation_z, avg_correlation_raw


def compute_parcel_homogeneity_blockwise(parcel_time_series, block_size=5000):
    """
    Compute the homogeneity for a single parcel based on its time series using a block-wise approach.
    """
    n_voxels = parcel_time_series.shape[1]
    total_sum_z = 0
    total_sum_raw = 0
    count = 0
    
    for i in range(0, n_voxels, block_size):
        block1 = parcel_time_series[:, i:i + block_size]
        
        correlations_within = np.corrcoef(block1, rowvar=False)
        correlations_within = np.clip(correlations_within, -0.999999, 0.999999)
        correlations_within_z = np.arctanh(correlations_within)
        
        total_sum_z += np.sum(correlations_within_z[np.triu_indices_from(correlations_within_z, k=1)])
        total_sum_raw += np.sum(correlations_within[np.triu_indices_from(correlations_within, k=1)])
        count += len(correlations_within[np.triu_indices_from(correlations_within_z, k=1)])
        
        for j in range(i + block_size, n_voxels, block_size):
            block2 = parcel_time_series[:, j:j + block_size]
            correlations_between = np.corrcoef(block1, block2, rowvar=False)[:block1.shape[1], block1.shape[1]:]
            correlations_between = np.clip(correlations_between, -0.999999, 0.999999)
            correlations_between_z = np.arctanh(correlations_between)
            
            total_sum_z += np.sum(correlations_between_z)
            total_sum_raw += np.sum(correlations_between)
            count += correlations_between.size
    
    avg_correlation_z = total_sum_z / count if count > 0 else np.nan
    avg_correlation_raw = total_sum_raw / count if count > 0 else np.nan
    return avg_correlation_z, avg_correlation_raw

def process_group_data(parcel_csv_dir, num_parcels=36, voxel_threshold=40000):
    """
    Compute the homogeneity within each parcel for the actual data and return parcel sizes.
    Process data in blocks only for parcels with more than voxel_threshold voxels.
    """
    parcel_homogeneities_z = {}
    parcel_homogeneities_raw = {}
    parcel_sizes = {}

    for parcel_id in range(1, num_parcels + 1):
        parcel_file = os.path.join(parcel_csv_dir, f'parcel_{parcel_id}_2d.csv')
        if os.path.exists(parcel_file):
            print(f"Processing {parcel_file}...")
            try:
                parcel_time_series = pd.read_csv(parcel_file, header=0).values
                num_voxels = parcel_time_series.shape[1]
                
                if num_voxels > voxel_threshold:
                    homogeneity_z, homogeneity_raw = compute_parcel_homogeneity_blockwise(parcel_time_series)
                else:
                    homogeneity_z, homogeneity_raw = compute_parcel_homogeneity(parcel_time_series)
                
                parcel_homogeneities_z[parcel_id] = homogeneity_z
                parcel_homogeneities_raw[parcel_id] = homogeneity_raw
                parcel_sizes[parcel_id] = num_voxels
            except Exception as e:
                print(f"Failed to process {parcel_file}: {e}")
        else:
            print(f"Parcel file {parcel_file} not found.")

    return parcel_homogeneities_z, parcel_homogeneities_raw, parcel_sizes

def region_growing(parcel_size, available_voxel_indices, shape):
    """
    Grow a region starting from a seed voxel, ensuring the parcel is contiguous and the correct size.
    """
    seed = available_voxel_indices[np.random.choice(len(available_voxel_indices))]
    grown_parcel = set([seed])
    growing_front = set([seed])
    
    while len(grown_parcel) < parcel_size and growing_front:
        new_voxel = growing_front.pop()
        grown_parcel.add(new_voxel)
        
        x, y, z = np.unravel_index(new_voxel, shape)
        neighbors = [
            np.ravel_multi_index((x + dx, y + dy, z + dz), shape)
            for dx, dy, dz in [(-1,0,0), (1,0,0), (0,-1,0), (0,1,0), (0,0,-1), (0,0,1)]
            if (0 <= x + dx < shape[0] and 0 <= y + dy < shape[1] and 0 <= z + dz < shape[2])
        ]
        for neighbor in neighbors:
            if neighbor in available_voxel_indices and neighbor not in grown_parcel:
                growing_front.add(neighbor)
    
    return list(grown_parcel)

def generate_spatially_contiguous_random_parcels(parcel_sizes, shape, original_labels):
    """
    Generate spatially contiguous random parcels with sizes matching those in `parcel_sizes`.
    """
    available_voxel_indices = np.where(original_labels > 0)[0]  # Exclude labels <= 0
    np.random.shuffle(available_voxel_indices)
    
    random_parcel = np.zeros(np.prod(shape), dtype=int)
    
    for parcel_id, size in parcel_sizes.items():
        grown_parcel = region_growing(size, available_voxel_indices, shape)
        random_parcel[grown_parcel] = parcel_id
        available_voxel_indices = np.setdiff1d(available_voxel_indices, grown_parcel)
    
    return random_parcel

def save_random_homogeneities(random_parcel, original_labels, tvalue_dir, num_parcels, voxel_threshold=40000):
    """
    Calculate and return the homogeneity metrics for the random parcels.
    """
    nifti_files = sorted(glob.glob(os.path.join(tvalue_dir, '*.nii.gz')))
    parcel_accumulated_data = {parcel_id: [] for parcel_id in range(1, num_parcels + 1)}
    
    for nifti_file in nifti_files:
        print(f"Processing {nifti_file}...")
        try:
            nifti_img = nib.load(nifti_file)
            data = nifti_img.get_fdata().flatten()

            for parcel_id in range(1, num_parcels + 1):
                random_mask = (random_parcel == parcel_id)
                voxel_indices = np.where(random_mask)[0]
                parcel_accumulated_data[parcel_id].append(data[voxel_indices])
        
        except Exception as e:
            print(f"Failed to process {nifti_file}: {e}")

    random_homogeneities_z = {}
    random_homogeneities_raw = {}
    weighted_homogeneity_sum_z = 0
    weighted_homogeneity_sum_raw = 0
    total_voxel_count = 0

    for parcel_id in range(1, num_parcels + 1):
        time_series_2d = np.stack(parcel_accumulated_data[parcel_id], axis=0)
        if time_series_2d.shape[1] > voxel_threshold:
            homogeneity_z, homogeneity_raw = compute_parcel_homogeneity_blockwise(time_series_2d)
        else:
            homogeneity_z, homogeneity_raw = compute_parcel_homogeneity(time_series_2d)

        random_homogeneities_z[parcel_id] = homogeneity_z
        random_homogeneities_raw[parcel_id] = homogeneity_raw
        weighted_homogeneity_sum_z += homogeneity_z * time_series_2d.shape[1]
        weighted_homogeneity_sum_raw += homogeneity_raw * time_series_2d.shape[1]
        total_voxel_count += time_series_2d.shape[1]

    group_average_homogeneity_z = weighted_homogeneity_sum_z / total_voxel_count if total_voxel_count > 0 else np.nan
    group_average_homogeneity_raw = weighted_homogeneity_sum_raw / total_voxel_count if total_voxel_count > 0 else np.nan

    return random_homogeneities_z, random_homogeneities_raw, group_average_homogeneity_z, group_average_homogeneity_raw

def process_randomizations(parcel_csv_dir, parcellation_file, tvalue_dir, num_parcels=36, num_randomizations=1000, voxel_threshold=40000):
    parcellation_img = nib.load(parcellation_file)
    original_labels = parcellation_img.get_fdata().flatten()
    shape = parcellation_img.shape
    
    _, _, parcel_sizes = process_group_data(parcel_csv_dir, num_parcels)

    all_random_homogeneities_z = []
    all_random_homogeneities_raw = []

    for rand_num in range(1, num_randomizations + 1):
        print(f"Processing randomization {rand_num}...")
        
        while True:
            random_parcel_labels = generate_spatially_contiguous_random_parcels(parcel_sizes, shape, original_labels)
            
            random_homogeneities_z, random_homogeneities_raw, group_average_homogeneity_z, group_average_homogeneity_raw = save_random_homogeneities(
                random_parcel_labels, original_labels, tvalue_dir, num_parcels, voxel_threshold
            )

            if not any(np.isnan(list(random_homogeneities_z.values()))):
                all_random_homogeneities_z.append(group_average_homogeneity_z)
                all_random_homogeneities_raw.append(group_average_homogeneity_raw)

                homogeneity_df = pd.DataFrame.from_dict(random_homogeneities_z, orient='index', columns=['Homogeneity_Z'])
                homogeneity_df['Homogeneity_Raw'] = pd.Series(random_homogeneities_raw)
                homogeneity_df['ParcelSize'] = pd.Series(parcel_sizes)
                output_csv = os.path.join(parcel_csv_dir, f'random_parcel_homogeneities_{rand_num}.csv')
                homogeneity_df.to_csv(output_csv)
                print(f"Saved random parcel homogeneities for randomization {rand_num} to {output_csv}")
                break
            else:
                print(f"Randomization {rand_num} had an invalid parcel homogeneity, retrying...")

    all_random_homogeneities_df = pd.DataFrame({
        'RandomGroupAverageHomogeneity_Z': all_random_homogeneities_z,
        'RandomGroupAverageHomogeneity_Raw': all_random_homogeneities_raw
    })
    all_random_homogeneities_df.to_csv(os.path.join(parcel_csv_dir, 'random_group_average_homogeneities.csv'), index=False)
    print(f"Saved all random group average homogeneities to {os.path.join(parcel_csv_dir, 'random_group_average_homogeneities.csv')}")


# Run (this is example for the association parcellation)
parcel_csv_dir = 'parcel_csv_files_parcelGrowing2'
parcellation_file = '/data/extra/movando/homo_group/association.nii.gz'
tvalue_dir = '/data/extra/movando/third-group/asso/randomisation'

process_randomizations(parcel_csv_dir, parcellation_file, tvalue_dir, num_parcels=36, num_randomizations=1000)

