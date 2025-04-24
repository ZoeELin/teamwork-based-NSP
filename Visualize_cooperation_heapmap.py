# Visualize_cooperation_heapmap.py

import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# <--- Edit parameter here --->
folder = "Output_baseline/n021w4"
file = "coop-intensity-12"
fig_title = " Cooperation Strength Heapmap"

# Collect all nurse IDs
all_nurses = set()
filepath = os.path.join(folder, f"{file}.json")
with open(filepath, "r") as f:
    data = json.load(f)
    for entry in data:
        all_nurses.update([entry["nurse1"], entry["nurse2"]])

# Sort nurse IDs
def nurse_sort_key(nurse_id):
    return int(nurse_id.split("_")[1])

all_nurses = sorted(all_nurses, key=nurse_sort_key)
reverse_nurses = sorted(all_nurses, key=nurse_sort_key, reverse=True)

# Initialize total matrix
intensity_matrix = pd.DataFrame(index=reverse_nurses, columns=all_nurses, data=0.0)

# Sum all matrices
with open(filepath, "r") as f:
    data = json.load(f)
    for entry in data:
        n1, n2 = entry["nurse1"], entry["nurse2"]
        score = entry["cooperation_score"]
        intensity_matrix.loc[n1, n2] += score
        intensity_matrix.loc[n2, n1] += score


# Plot the average heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(
    intensity_matrix,
    cmap="YlGnBu",
    square=True,
    linewidths=0.3,
    linecolor="gray",
    cbar=True,
    xticklabels=True,
    yticklabels=True
)

plt.title(fig_title, fontsize=18)
plt.tight_layout()
plt.show()

# Save the figure
save_path = os.path.join(folder, f"{file}.png")
plt.savefig(save_path)
print(f"Saved average heatmap to {save_path}")