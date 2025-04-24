import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from collections import defaultdict

# Set the folder containing JSON files, output path, output file name and the number of files to process
# <--- Edit parameter here --->
folder = "Output_baseline/n021w4" 
n_files = 12
# pre_filename = "coop-intensity-ComC100" 
pre_filename = "coop-intensity" 
# fig_title = "Cooperation Strength Based on SA with ComC:100 Algorithm" 
fig_title = "Cooperation Strength Based on SA Algorithm" 
# output_filename = "ComC100-SA-based_coop_evolution_run12times.png"
output_filename = "SA-based_coop_evolution_run12times.png"


# Collect all nurse IDs
all_nurses = set()
heatmaps = []

# Collect all nurses set
for i in range(1, n_files + 1):
    filepath = os.path.join(folder, f"{pre_filename}-{i}.json")
    with open(filepath, "r") as f:
        data = json.load(f)
        # scores = defaultdict(float)
        for entry in data:
            n1, n2 = entry["nurse1"], entry["nurse2"]
            # key = tuple(sorted([n1, n2]))
            # scores[key] = entry["cooperation_score"]
            all_nurses.update([n1, n2])


# Sort the nurses by their IDs
def nurse_sort_key(nurse_id):
    return int(nurse_id.split("_")[1])


all_nurses = sorted(all_nurses, key=nurse_sort_key)
reverse_nurses = sorted(all_nurses, key=nurse_sort_key, reverse=True)


# Reconstruct the heatmap matrix from the cooperation data
for i in range(1, n_files + 1):
    filepath = os.path.join(folder, f"{pre_filename}-{i}.json")
    with open(filepath, "r") as f:
        data = json.load(f)
        matrix = pd.DataFrame(index=reverse_nurses, columns=all_nurses, data=0.0)
        for entry in data:
            n1, n2 = entry["nurse1"], entry["nurse2"]
            score = entry["cooperation_score"]
            matrix.loc[n1, n2] = score
            matrix.loc[n2, n1] = score
        heatmaps.append(matrix)


# Calculate the minimum and maximum values of all heatmaps 
vmin = min(h.values.min().min() for h in heatmaps)
vmin = 0
vmax = max(h.values.max().max() for h in heatmaps)

# Set figure and subgraph
fig, axes = plt.subplots(3, 4, figsize=(20, 15))
fig.suptitle(fig_title, fontsize=20)

# Draw subgraph
for idx, ax in enumerate(axes.flat):
    sns.heatmap(
        heatmaps[idx],
        cmap="YlGnBu",
        square=True,
        linewidths=0.3,
        linecolor="gray",
        cbar=True,  # Show colorbar
        ax=ax,
        xticklabels=True,
        yticklabels=True,
        vmin=vmin,  # Unified color scale (standardize the color range)
        vmax=vmax,
    )
    ax.set_title(f"{idx + 1}th Schedule's Cooperation Matrix")

plt.tight_layout(rect=[0, 0, 1, 0.96])

# Save the figure
plt.savefig(os.path.join(folder, output_filename))
print(f"Saved heatmap to {os.path.join(folder, output_filename)}")
