import json
import os
import matplotlib.pyplot as plt

# ========================================
# 📌 說明：
# 這支程式會讀取多個 simulation 結果中的「合作強度 JSON 檔」，
# 每個 JSON 檔記錄某次模擬中各對護士 (nurse pairs) 的合作強度分數。
# 程式會統整所有護士配對的合作強度變化，
# 並用折線圖繪出每對護士在多次模擬中的合作強度趨勢。
# 圖片最後會儲存成 PNG 檔案。
# ========================================


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
            all_data[nurse_pair] = []
        all_data[nurse_pair].append(entry["cooperation_score"])

# 畫折線圖
plt.figure(figsize=(12, 8))

for nurse_pair, values in all_data.items():
    plt.plot(range(1, num_files + 1), values, label=str(nurse_pair))  # ✅ 修正 warning

plt.xlabel("Simulation Number")
plt.ylabel("Cooperation Intensity")
plt.title(f"Each Nurse Pair Cooperation Intensity Over Simulations with ComC penalty({weight})")

# ✅ legend 移到圖外
# plt.legend(fontsize="small", bbox_to_anchor=(1.05, 1), loc="upper left")

# ✅ 自動調整 layout，如果太滿可以改用 subplots_adjust
plt.tight_layout()

# ✅ 儲存圖片
output_path = os.path.join(folder, output_file_name)
plt.savefig(output_path, dpi=300, bbox_inches="tight")  # 儲存高畫質圖片

plt.grid(True)
plt.show()

print(f"✅ 圖片已儲存至：{output_path}")
