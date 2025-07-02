#!/bin/bash

#SBATCH --mem=64G
#SBATCH --time=3-00:00:00
#SBATCH --chdir=.
#SBATCH --job-name=Movie1


# Set input and output directories (same folder)
input_dir="/scratch/movando/movie/all_preprocessed_v2"
output_dir="${input_dir}/2mm"
mkdir -p "$output_dir"

# Reference image for MNI 2mm brain
ref_img="/scratch/movando/movie/all_preprocessed/MNI152_T1_2mm_brain.nii.gz"

# Specify the file you want to process (e.g., sub-10_task-500daysofsummer_bold_preprocessedICA.nii)
file="/scratch/movando/movie/all_preprocessed_v2/sub-1_task-500daysofsummer_bold_bold_blur_censor_ica.nii"

# Get the filename and create the output filename
filename=$(basename "$file")
base="${filename%.nii}"
output_file="${output_dir}/${base}_2mm.nii"

echo "🔁 Resampling $filename → ${base}_2mm.nii"

# Run flirt for the specified file
flirt -in "$file" \
      -ref "$ref_img" \
      -applyisoxfm 2.0 \
      -nosearch \
      -out "$output_file"

echo "✅ Done resampling the file to 2mm."
