import json
import os
import matplotlib.pyplot as plt

# 你放 coop-intensity-*.json 的資料夾
folder = "Output_dataset/n040w4"

# 讀取所有 coop-intensity json檔
num_files = 12
all_data = {}

for i in range(1, num_files + 1):
    file_path = os.path.join(folder, f"coop-intensity-{i}.json")
    with open(file_path, "r") as f:
        data = json.load(f)

    for entry in data:
        nurse_pair = tuple(sorted((entry["nurse1"], entry["nurse2"])))
        if (nurse_pair) not in all_data:
            all_data[nurse_pair] = []
        all_data[nurse_pair].append(entry["cooperation_score"])

# 畫折線圖
plt.figure(figsize=(12, 8))

for nurse_pair, values in all_data.items():
    plt.plot(range(1, num_files + 1), values, label=nurse_pair)

plt.xlabel("Simulation Number")
plt.ylabel("Cooperation Intensity")
plt.title("Nurse Pair Cooperation Intensity Over Simulations")
plt.legend(
    fontsize="small", bbox_to_anchor=(1.05, 1), loc="upper left"
)  # 把 legend 放旁邊，不擠
plt.tight_layout()
plt.grid(True)
plt.show()
