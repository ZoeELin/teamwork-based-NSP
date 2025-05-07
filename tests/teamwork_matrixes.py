import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 設定資料夾與 JSON 檔案名稱
solution_folder = "testdatasets_json/n005w4/Solution_H_0-WD_1-2-3-3"

# 讀取該資料夾內的所有 .json 檔案
json_files = [f for f in os.listdir(solution_folder) if f.endswith(".json")]


# 解析 JSON 數據
nurses = set()
cooperation_matrices = {}

for json_file in json_files:
    file_path = os.path.join(solution_folder, json_file)

    with open(file_path, "r") as f:
        data = json.load(f)

    assignments = data["assignments"]
    nurses.update(a["nurse"] for a in assignments)

    # 建立合作矩陣
    nurse_list = sorted(nurses)
    cooperation_matrix = pd.DataFrame(0, index=nurse_list, columns=nurse_list)

    shifts_by_day = {}
    for assign in assignments:
        key = (assign["day"], assign["shiftType"])
        if key not in shifts_by_day:
            shifts_by_day[key] = []
        shifts_by_day[key].append(assign["nurse"])

    for nurses_in_shift in shifts_by_day.values():
        for i, nurse1 in enumerate(nurses_in_shift):
            for j in range(i + 1, len(nurses_in_shift)):
                nurse2 = nurses_in_shift[j]
                cooperation_matrix.loc[nurse1, nurse2] += 1
                cooperation_matrix.loc[nurse2, nurse1] += 1

    cooperation_matrices[json_file] = cooperation_matrix

# 計算合作指標
results = []

for json_file, coop_matrix in cooperation_matrices.items():
    stats = {"solution": json_file}

    # 合作穩定性 (主要合作夥伴占比)
    stability_scores = []
    diversity_scores = []
    total_cooperations = []

    for nurse in nurses:
        partnerships = coop_matrix.loc[nurse]
        total_coop = partnerships.sum()

        if total_coop > 0:
            main_partner = partnerships.idxmax()
            main_partner_count = partnerships.max()
            stability_score = main_partner_count / total_coop  # 主要合作夥伴占比
            diversity_score = (partnerships > 0).sum() / (
                len(nurses) - 1
            )  # 獨特合作夥伴比例
        else:
            stability_score = 0
            diversity_score = 0

        stability_scores.append(stability_score)
        diversity_scores.append(diversity_score)
        total_cooperations.append(total_coop)

    # 計算平均穩定性 & 多樣性
    stats["avg_stability"] = np.mean(stability_scores)
    stats["avg_diversity"] = np.mean(diversity_scores)

    # 計算合作均衡性 (標準差)
    stats["cooperation_balance"] = np.std(total_cooperations)

    results.append(stats)

# 轉換為 DataFrame 並輸出結果
results_df = pd.DataFrame(results)

fig, ax = plt.subplots(figsize=(8, 4))
ax.axis("off")
table = ax.table(
    cellText=results_df.values,
    colLabels=results_df.columns,
    cellLoc="center",
    loc="center",
)
plt.title("Nurse Cooperation Metrics")

output_png_path = os.path.join(solution_folder, "nurse_cooperation_metrics.png")
plt.savefig(output_png_path, bbox_inches="tight", dpi=300)
plt.show()

print(f"合作指標表格已儲存至: {output_png_path}")
