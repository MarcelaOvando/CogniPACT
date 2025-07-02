import os
import glob
import numpy as np
import pandas as pd
import nibabel as nib

# This script extracts voxel data from 3D NIfTI images according to our parcellation, 
# aggregates voxel values across multiple time points, and saves parcel-specific 
# 2D time series matrices as CSV files for downstream analysis.


def nifti_to_2d_by_parcel(nifti_file, parcel_labels):
    nifti_img = nib.load(nifti_file)
    data = nifti_img.get_fdata()  # Shape: (x, y, z)
    
    # Flatten the 3D image to a 1D array for voxel data
    data_flat = data.flatten()

    # Flatten parcel labels to match voxel data
    parcel_labels_flat = parcel_labels.flatten()
    
    # Group voxel data by parcel, excluding unwanted labels
    parcels = np.unique(parcel_labels_flat)
    parcel_data = {}
    
    for parcel in parcels:
        if parcel > 0:  # Exclude labels <= 0, or modify this condition as needed
            voxel_indices = np.where(parcel_labels_flat == parcel)[0]
            parcel_data[parcel] = data_flat[voxel_indices]
    
    return parcel_data


def process_time_series_by_parcel(tvalue_dir, nifti_label_file, output_dir):
    # Load parcel labels
    parcel_img = nib.load(nifti_label_file)
    parcel_labels = parcel_img.get_fdata().astype(int)  # Ensure labels are integers
    
    # Initialize a dictionary to store accumulated data for each parcel
    parcel_accumulated_data = {}

    # Find all NIfTI files in the directory (one for each time point)
    nifti_files = sorted(glob.glob(os.path.join(tvalue_dir, '*.nii.gz')))
    
    for nifti_file in nifti_files:
        print(f"Processing {nifti_file}...")
        try:
            # Get parcel-wise voxel data for the current time point
            parcel_data = nifti_to_2d_by_parcel(nifti_file, parcel_labels)
            
            # Accumulate data across time points
            for parcel, data_1d in parcel_data.items():
                if parcel not in parcel_accumulated_data:
                    parcel_accumulated_data[parcel] = []
                parcel_accumulated_data[parcel].append(data_1d)
        
        except Exception as e:
            print(f"Failed to process {nifti_file}: {e}")

    # Convert accumulated data to CSV files
    for parcel, time_series_data in parcel_accumulated_data.items():
        # Stack the list of 1D arrays into a 2D array (time points x voxels)
        time_series_2d = np.stack(time_series_data, axis=0)
        
        # Save the accumulated data for this parcel
        output_file = os.path.join(output_dir, f'parcel_{parcel}_2d.csv')
        pd.DataFrame(time_series_2d).to_csv(output_file, index=False)
        file_size = os.path.getsize(output_file)
        print(f"Saved parcel {parcel} data to {output_file} ({file_size / (1024 * 1024):.2f} MB)")

# Example usage
tvalue_dir = '/data/extra/movando/third-group/asso/randomisation'  # Directory containing your 3D t-value files for each time point
nifti_label_file = 'association.nii.gz'  # Your parcellation file
output_dir = 'parcel_csv_files'  # Directory to save the CSV files

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Process the NIfTI files and save parcel data to CSV files
process_time_series_by_parcel(tvalue_dir, nifti_label_file, output_dir)

