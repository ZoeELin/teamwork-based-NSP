# Plot_average_coop_heapmap.py
# 📌 功能：本程式會讀取多次（12 次）模擬結果中的「合作強度 JSON 檔案」，
#        計算所有護士配對的平均合作強度，並以熱圖（Heatmap）方式呈現，
#        最後將圖像儲存為 PNG 圖片。

import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# <--- Edit parameter here --->
folder = "Output0429/n021w4"
n_files = 12
pre_filename = "coop-intensity-comc150"
fig_title = "Average Cooperation Strength (ComC:150)"
output_filename = "SA-based_with_ComC_w150_coop_average_runs.png"

# Collect all nurse IDs
all_nurses = set()
for i in range(1, n_files + 1):
    filepath = os.path.join(folder, f"{pre_filename}-{i}.json")
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
average_matrix = pd.DataFrame(index=reverse_nurses, columns=all_nurses, data=0.0)

# Sum all matrices
for i in range(1, n_files + 1):
    filepath = os.path.join(folder, f"{pre_filename}-{i}.json")
    with open(filepath, "r") as f:
        data = json.load(f)
        for entry in data:
            n1, n2 = entry["nurse1"], entry["nurse2"]
            score = entry["cooperation_score"]
            average_matrix.loc[n1, n2] += score
            average_matrix.loc[n2, n1] += score

# Divide by number of files to get the average
average_matrix /= n_files

# Plot the average heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(
    average_matrix,
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
save_path = os.path.join(folder, output_filename)
plt.savefig(save_path)
print(f"Saved average heatmap to {save_path}")