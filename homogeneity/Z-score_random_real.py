import numpy as np
import pandas as pd

# Load the CSV file containing the random homogeneities
csv_file = 'random1000/random_group_average_homogeneities.csv'
column_name = 'RandomGroupAverageHomogeneity_Z'

# Read the specific column from the CSV file
random_homogeneities = pd.read_csv(csv_file)[column_name].values

# Calculate the mean and standard deviation of the random homogeneities
mean_random_homogeneity = np.mean(random_homogeneities)
std_random_homogeneity = np.std(random_homogeneities)

# Define the real homogeneity value (this is the value of my actual parcellation)
real_homogeneity = 0.9186076421808436  # Replace this with your actual real homogeneity value

# Calculate and print the Z-score
z_score = (real_homogeneity - mean_random_homogeneity) / std_random_homogeneity

print(f"Z-score: {z_score}")

# to add the permutation calculation
all_values = random_homogeneities + [real_homogeneity]
observed_diff = real_homogeneity - np.mean(random_homogeneities)

n_permutations = 10000
count = 0

for _ in range(n_permutations):
    np.random.shuffle(all_values)
    new_real_homogeneity = all_values[-1]
    new_random_mean = np.mean(all_values[:-1])
    
    if abs(new_real_homogeneity - new_random_mean) >= abs(observed_diff):
        count += 1

p_value = count / n_permutations
print(f"Permutation test p-value: {p_value}")

