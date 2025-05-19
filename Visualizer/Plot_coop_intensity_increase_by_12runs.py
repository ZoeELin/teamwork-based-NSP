import json
import os
import matplotlib.pyplot as plt


# Edit these variables
folder = "Output-weight50-50-1000/n100w4" # <-- Edit this to your coop-intensity folder
output_file_name = "coop-intensity-with-comc1000.png"  # <-- Edit this to your output file name
read_json_pre_filename = "coop-intensity-comc1000"  # <-- Edit this to your json file name prefix
weight = 1000


# ----------------------------------------
# 讀取所有 coop-intensity json檔
num_files = 12
all_data = {}

for i in range(1, num_files + 1):
    # file_path = os.path.join(folder, f"coop-intensity-{i}.json")
    file_path = os.path.join(folder, f"{read_json_pre_filename}-{i}.json")
    with open(file_path, "r") as f:
        data = json.load(f)

    for entry in data:
        nurse_pair = tuple(sorted((entry["nurse1"], entry["nurse2"])))
        if (nurse_pair) not in all_data:
            all_data[nurse_pair] = [0.0]
        all_data[nurse_pair].append(entry["cooperation_score"])

# 畫折線圖
plt.figure(figsize=(12, 8))
base_color = "#1f77b4"

for nurse_pair, values in all_data.items():
    plt.plot(range(len(values)), values, label=str(nurse_pair), color=base_color, linewidth=0.1, alpha=0.5)

plt.xticks(range(len(values)))  # x軸: 0 ~ num_files
plt.yticks(range(0, int(max(max(v) for v in all_data.values())) + 2))  # y軸: 0 ~ max value + 1

plt.xlabel("Simulation Number")
plt.ylabel("Cooperation Intensity")
plt.title(f"Each Nurse Pair Cooperation Intensity Over Simulations with ComC penalty({weight})")

# legend 移到圖外
# plt.legend(fontsize="small", bbox_to_anchor=(1.05, 1), loc="upper left")


plt.grid(True, which='both', linestyle='--', alpha=0.3)
plt.tight_layout()

# 儲存圖片
plt.savefig(output_file_name, dpi=300, bbox_inches="tight")  # 儲存高畫質圖片

plt.grid(True)
plt.show()

print(f"✅ 圖片已儲存至：{output_file_name}")
