#!/bin/bash


#SBATCH --mem=64G
#SBATCH --time=6-00:00:00
#SBATCH --chdir=.
#SBATCH --job-name=NBD1
#SBATCH --cpus-per-task=12



# This file concatenates each concept-related concept across subjects
# The output of this script is a 4D file with 8 volumes (1 per subject) per concept

BASE_DIR="/scratch/movando/merged_NBS"
OUTPUT_DIR="/scratch/movando/concatenated_NBS"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "Starting prefix-based concatenation..."
echo "======================================="

# Find subdirectories (sub1 to sub8)
subdirs=($(find "$BASE_DIR" -mindepth 1 -maxdepth 1 -type d | sort))

# Use first subject's files to extract prefixes
cd "${subdirs[0]}" || exit
prefixes=$(ls *.nii.gz | sed -E 's/(_[0-9]+\.nii\.gz)$//' | sort | uniq)

# Process each unique prefix
for prefix in $prefixes; do
    files_to_merge=()
    echo ""
    echo "Searching for files starting with: $prefix in each sub..."

    for sub in "${subdirs[@]}"; do
        match=$(find "$sub" -maxdepth 1 -type f -name "${prefix}_*.nii.gz" | head -n 1)
        if [ -n "$match" ]; then
            files_to_merge+=("$match")
        else
            echo "No match in: $sub"
        fi
    done

    if [ "${#files_to_merge[@]}" -eq 8 ]; then
        echo "Found in all 8 subfolders. Concatenating:"
        for f in "${files_to_merge[@]}"; do
            echo "   - $f"
        done

        output_file="$OUTPUT_DIR/${prefix}.nii.gz"
        fslmerge -t "$output_file" "${files_to_merge[@]}"
        echo "➡️  Output saved to: $output_file"

        # Check number of volumes
        num_vols=$(fslval "$output_file" dim4)
        if [ "$num_vols" -eq 8 ]; then
            echo "Volume check passed: $num_vols volumes"
        else
            echo "Volume check failed: found $num_vols (expected 8)"
        fi
        echo "-------------------------------------------"
    else
        echo "Skipping $prefix: found in ${#files_to_merge[@]} subfolders (expected 8)"
        echo "-------------------------------------------"
    fi
done

echo ""
echo "Prefix-based concatenation complete."
