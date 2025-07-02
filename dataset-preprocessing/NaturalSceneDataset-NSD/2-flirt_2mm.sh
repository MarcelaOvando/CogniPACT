#!/bin/bash

#SBATCH --mem=32G
#SBATCH --time=3-00:00:00
#SBATCH --chdir=.
#SBATCH --cpus-per-task=12
#SBATCH --job-name=AllFlirt

# Base directory where all subfolders (sub1 to sub8) are located
base_dir="/scratch/movando/NBS"

# Reference image
ref_img="/scratch/movando/movie/all_preprocessed/MNI152_T1_2mm_brain.nii.gz"

# Loop over subjects
for subj in sub{1..8}; do
    subj_dir="${base_dir}/${subj}"

    # Loop over sessions
    for sess_num in {1..30}; do
        session_name=$(printf "session%02d" $sess_num)  # This ensures two-digit session names
        session_dir="${subj_dir}/${session_name}"

        # Check if the session folder exists
        if [ ! -d "$session_dir" ]; then
            echo "Skipping missing $session_dir"
            continue
        fi

        echo "Processing $session_dir"

        # Create output folder
        output_dir="${session_dir}/2mm"
        mkdir -p "$output_dir"

        # Process all timeseries_*.nii.gz files
        session_num_padded=$(printf "%02d" $sess_num)
        for file in "$session_dir"/timeseries_session${session_num_padded}_run*.nii.gz; do
            [ -e "$file" ] || continue  # skip if no match
            filename=$(basename "$file")
            base="${filename%.nii.gz}"
            output_file="${output_dir}/${base}_2mm.nii.gz"

            echo "↪️ Resampling $filename → ${base}_2mm.nii.gz"

            flirt -in "$file" \
                  -ref "$ref_img" \
                  -applyisoxfm 2.0 \
                  -nosearch \
                  -out "$output_file"
        done
    done
done

echo "All files resampled to 2mm."
