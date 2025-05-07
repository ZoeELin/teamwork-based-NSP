import re
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# 設定 log 檔案位置
log_file = "logs-n03040test-0507/n040w8/scheduler_ComCw0_run2_20250507_125820.txt"
scenario = "n040w8"
filename = f"temperature_vs_penalty_per_week-{scenario}-2.png"

# 儲存每週的溫度與懲罰值
week_data = {}  # e.g., {0: [(temp1, penalty1), (temp2, penalty2)], 1: [...], ...}
# week_data_neighbor = {}  # e.g., {(week0, temp1): [penalty1, penalty2], ...}

current_week = None
current_temp = None


# 讀取並解析 log
with open(log_file, "r") as f:
    for line in f:
        # 檢查是否切換到新的 week
        week_match = re.search(r'Processing: week (\d+)', line)
        if week_match:
            current_week = int(week_match.group(1))
            if current_week not in week_data:
                week_data[current_week] = []

        # 讀取當前溫度
        temp_match = re.search(r'> Current temperature: ([\d\.]+), current penalties: (\d+)', line)
        if temp_match:
            current_temp = float(temp_match.group(1))
            current_penalty = int(temp_match.group(2)) 
            week_data[current_week].append((current_temp, current_penalty))

        # # 讀取鄰懲罰值並記錄到對應 week
        # neighbor_penalty_match = re.search(r'penalties (\d+)', line)
        # neighbor = []
        # if neighbor_penalty_match and current_temp is not None and current_week is not None:
        #     penalties = int(neighbor_penalty_match.group(1))
        #     neighbor.append(penalties)



# 畫圖
plt.figure(figsize=(12, 7))

# 顏色配置
cmap = cm.get_cmap('tab10')  # 最多支援10個不同顏色（超過也會重複）


all_temperatures = set()

for i, (week, data) in enumerate(sorted(week_data.items())):
    temps, pens = zip(*data)
    all_temperatures.update(temps)
    plt.plot(
        temps,
        pens,
        marker='o',
        markersize=3,         # ✅ 點變小
        linewidth=1,          # ✅ 線條細
        alpha=0.5,            # ✅ 半透明線
        label=f"Week {week}",
        color=cmap(i % 10)
    )

# 加上垂直線在每個 temperature 上
for t in sorted(all_temperatures):
    plt.axvline(x=t, color='gray', linestyle=':', linewidth=0.5, alpha=0.3)  # ✅ 垂直線

# 圖表格式
plt.xlabel("Temperature")
plt.ylabel("Penalty")
plt.title(f"Temperature vs Penalty for Each Week during Simulated Annealing in {scenario}")
plt.grid(True)
plt.gca().invert_xaxis()
plt.legend(title="Week")
plt.tight_layout()

# 儲存與顯示
plt.savefig(filename, dpi=300)
plt.show()