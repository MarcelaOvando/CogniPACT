#!/bin/bash


#SBATCH --mem=64G
#SBATCH --time=6-00:00:00
#SBATCH --chdir=.
#SBATCH --job-name=NBD1
#SBATCH --cpus-per-task=12

# This file averages the 6 volumes per concept per subject
# this is the script for S1
# Set input and output directories
INPUT_DIR="/scratch/movando/NBS_vols_index/sub1"
OUTPUT_DIR="/scratch/movando/merged_NBS/sub1"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Move into input directory
cd "$INPUT_DIR" || exit

echo "Starting mean image computation..."
echo "=================================="

# Find all unique prefixes like IMG0003_3050
for prefix in $(ls *.nii.gz | sed -E 's/(_session.*)//' | sort | uniq); do
    # Find all files with that prefix
    files=(${prefix}_session*run*vol*shown*.nii.gz)

    # Check if there are exactly 3 files
    if [ "${#files[@]}" -eq 3 ]; then
        echo ""
        echo "Computing mean for prefix: $prefix"
        for file in "${files[@]}"; do
            echo "   - $file"
        done

        # Define output file path
        output_file="${OUTPUT_DIR}/${prefix}.nii.gz"

        # Step 1: Merge into 4D volume
        fslmerge -t temp_merged.nii.gz "${files[@]}"

        # Step 2: Compute mean across all 6 timepoints
        fslmaths temp_merged.nii.gz -Tmean "$output_file"

        # Clean up
        rm temp_merged.nii.gz

        echo "Mean saved to: $output_file"
        echo "----------------------------------"
    else
        echo ""
        echo "Skipping $prefix: found ${#files[@]} files (expected 3)"
        echo "----------------------------------"
    fi
done

echo ""
echo "✅ Mean computation completed."
