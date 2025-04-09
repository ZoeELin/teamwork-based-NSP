import json
import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict


# 設定資料夾與 JSON 檔案名稱
solution_folder = "testdatasets_json/n005w4/Solution_H_0-WD_1-2-3-3"

# 讀取該資料夾內的所有 .json 檔案
json_files = [f for f in os.listdir(solution_folder) if f.endswith(".json")]

# 解析 JSON 數據
nurses = set()
cooperation_matrices = {}

for json_file in json_files:
    file_path = os.path.join(solution_folder, json_file)

    # 讀取 JSON 檔案
    with open(file_path, "r") as f:
        data = json.load(f)

    # 取得護士與排班資訊
    assignments = data["assignments"]
    nurses.update(a["nurse"] for a in assignments)

    # 計算護士合作關係
    shifts_by_day = defaultdict(list)
    for assign in assignments:
        shifts_by_day[(assign["day"], assign["shiftType"])].append(assign["nurse"])

    # 建立合作矩陣
    nurse_list = sorted(nurses)
    cooperation_matrix = pd.DataFrame(0, index=nurse_list, columns=nurse_list)

    for (day, shift), working_nurses in shifts_by_day.items():
        for i, nurse1 in enumerate(working_nurses):
            for j in range(i + 1, len(working_nurses)):
                nurse2 = working_nurses[j]
                cooperation_matrix.loc[nurse1, nurse2] += 1
                cooperation_matrix.loc[nurse2, nurse1] += 1

    cooperation_matrices[json_file] = cooperation_matrix

# 視覺化護士合作關係圖並儲存圖片，並在邊 (edge) 上加上合作次數
fig, axes = plt.subplots(
    len(cooperation_matrices), 1, figsize=(8, len(cooperation_matrices) * 4)
)

for idx, (file_name, coop_matrix) in enumerate(cooperation_matrices.items()):
    G = nx.Graph()

    for nurse1 in nurse_list:
        for nurse2 in nurse_list:
            weight = int(coop_matrix.loc[nurse1, nurse2])
            if nurse1 != nurse2 and weight > 0:
                G.add_edge(nurse1, nurse2, weight=weight)

    ax = axes[idx] if len(cooperation_matrices) > 1 else axes
    pos = nx.spring_layout(G, seed=42)
    edges = G.edges(data=True)
    weights = [d["weight"] for (_, _, d) in edges]

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=1000,
        node_color="lightblue",
        edge_color="gray",
        width=2,
        font_size=5,
        ax=ax,
    )
    edge_labels = {(u, v): f"{d['weight']}" for u, v, d in edges}
    nx.draw_networkx_edge_labels(
        G,
        pos=nx.spring_layout(G, seed=42, k=0.5),
        edge_labels=edge_labels,
        font_size=15,
        ax=ax,
    )

    ax.set_title(file_name)

# 儲存圖片
output_path = os.path.join(solution_folder, "nurse_graph.png")
plt.suptitle("Nurse Cooperation Graph", fontsize=14)
plt.savefig(output_path, bbox_inches="tight")
plt.show()

print(f"護士合作關係圖已儲存至: {output_path}")
