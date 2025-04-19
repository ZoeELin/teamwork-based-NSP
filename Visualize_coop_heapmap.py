import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from collections import defaultdict

# 設定資料夾與檔案數量
folder = "Output/n021w4"
n_files = 12

# 預先收集所有護士，確保 axis 排列一致
all_nurses = set()
heatmaps = []

# 收集所有護士名單和每次模擬的合作矩陣
for i in range(1, n_files + 1):
    filepath = os.path.join(folder, f"coop-intensity-{i}.json")
    with open(filepath, "r") as f:
        data = json.load(f)
        scores = defaultdict(float)
        for entry in data:
            n1, n2 = entry["nurse1"], entry["nurse2"]
            key = tuple(sorted([n1, n2]))
            scores[key] = entry["cooperation_score"]
            all_nurses.update([n1, n2])

def nurse_sort_key(nurse_id):
    return int(nurse_id.split("_")[1])

# 轉為有序名單
all_nurses = sorted(all_nurses, key=nurse_sort_key)
print(f"All nurses: {all_nurses}")
reverse_nurses = sorted(all_nurses, key=nurse_sort_key, reverse=True)

# 重新建構每一輪的 heatmap 矩陣
for i in range(1, n_files + 1):
    filepath = os.path.join(folder, f"coop-intensity-{i}.json")
    with open(filepath, "r") as f:
        data = json.load(f)
        matrix = pd.DataFrame(index=reverse_nurses, columns=all_nurses, data=0.0)
        for entry in data:
            n1, n2 = entry["nurse1"], entry["nurse2"]
            score = entry["cooperation_score"]
            matrix.loc[n1, n2] = score
            matrix.loc[n2, n1] = score
        heatmaps.append(matrix)

# 設定畫布與子圖
fig, axes = plt.subplots(3, 4, figsize=(20, 15))
fig.suptitle("Cooperation Strength over 12 Simulations", fontsize=20)

# 統一色彩比例方便比較
vmin = min(h.values.min().min() for h in heatmaps)
vmax = max(h.values.max().max() for h in heatmaps)

# 畫出每一張子圖
for idx, ax in enumerate(axes.flat):
    sns.heatmap(
        heatmaps[idx],
        cmap="YlGnBu",
        square=True,
        linewidths=0.3,
        linecolor='gray',
        cbar=False,
        ax=ax,
        xticklabels=True,
        yticklabels=True,
        vmin=vmin,
        vmax=vmax
    )
    ax.set_title(f"{idx + 1}th Schedule's Cooperation Matrix")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(os.path.join(folder, "coop_evolution_run12times.png"))
print(f"Saved heatmap to {os.path.join(folder, 'coop_evolution_12.png')}")
plt.show()