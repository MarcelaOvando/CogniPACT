# This is to concatenate and save the two volumes per concept per subject at each repetition (3 times per subject)
# The output are 6 files (2-volumes each) per concept per subject
# this is the script for S1

import os
import pandas as pd
import nibabel as nib
from pathlib import Path

# Paths 
excel_path = "/scratch/movando/NBS/sub1/Sub_01_info.xlsx"  # Replace with your Excel file path
nifti_base_path = "/scratch/movando/NBS/preprocessed_output/preprocessing_sub1"  # Base path where session folders are
output_dir = "/scratch/movando/NBS_vols_index/sub1"  # Output directory for 2-volume files
os.makedirs(output_dir, exist_ok=True)

# Load file
df = pd.read_excel(excel_path)

# Loop through each row in the Excel file
for idx, row in df.iterrows():
    index_MOT = str(row["index_MOT"])
    index = str(row["index"])
    subject = str(row["subject"])
    session = int(row["session"])
    run = int(row["run"])
    real_volume = int(row["real-volume"]) - 1  # Convert to 0-based indexing
    shown = str(row["shown"])  # Can be '1', '2', or '3'

    # Pad session and run numbers with zeros
    session_str = f"{session:02d}"
    run_str = f"{run:02d}"

    # Construct path to session folder and the specific time series file
    session_folder = os.path.join(nifti_base_path, f"session{session_str}")
    nifti_path = os.path.join(session_folder, f"timeseries_session{session_str}_run{run_str}", f"timeseries_session{session_str}_run{run_str}_2mm.nii.gz")

    # Check if the session folder and file exist
    if not os.path.exists(nifti_path):
        print(f"⚠️ File not found: {nifti_path}")
        continue

    # Load the NIfTI file
    img = nib.load(nifti_path)
    data = img.get_fdata()

    # Check if the volume index is within range
    if real_volume + 2 > data.shape[3]:
        print(f"⚠️ Not enough volumes in {nifti_path} for real_volume {real_volume}")
        continue

    # Extract 2 volumes
    extracted_data = data[..., real_volume:real_volume + 2]

    # Create new NIfTI image
    new_img = nib.Nifti1Image(extracted_data, affine=img.affine, header=img.header)

    # Output filename with 'shown'
    output_filename = f"{index_MOT}_{index}_{subject}_session{session_str}_run{run_str}_vol{real_volume+1}_shown{shown}.nii.gz"
    output_path = os.path.join(output_dir, output_filename)

    # Save the new file
    nib.save(new_img, output_path)
    print(f"Saved: {output_path}")
