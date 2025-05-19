import re
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# filepath = "processed/soft_penalty_summary_n030w4.txt"
filepath = "soft_penalty_summary_n030w4_weight0_250.txt"
scenario = "n030w4"


# 讀取文字檔案
with open(filepath, "r") as f:
    text_data = f.read()

# 解析格式：ComC、Week、Penalty
pattern = re.compile(r"(\d+)\s+(\d)\s+([\d\.]+)")
matches = pattern.findall(text_data)

# 建立 DataFrame
df = pd.DataFrame(matches, columns=["ComC", "Week", "Penalty"])
df["ComC"] = df["ComC"].astype(int)
df["Week"] = df["Week"].astype(int)
df["Penalty"] = df["Penalty"].astype(float)

# 建立 pivot 表格方便畫出各週 penalty 變化
pivot_df = df.pivot(index="ComC", columns="Week", values="Penalty")

# 計算每個 ComC weight 的總和
total_penalties = pivot_df.sum(axis=1)

# 印出總和值以供確認
print("\n每個 ComC weight 的總和值：")
for comc, total in total_penalties.items():
    print(f"ComC {comc}: {total:.2f}")

# 繪圖
fig, ax2 = plt.subplots(figsize=(12, 6))

# 將索引轉換為 numpy array
x_values = pivot_df.index.values

# 建立第二個 y 軸來畫折線圖
ax1 = ax2.twinx()

# 先畫 bar chart（背景）
bars = ax2.bar(x_values, total_penalties.values, alpha=1, color='lightgray', label='Total Penalty', width=10, zorder=10)
ax2.set_ylabel("Total Penalty")

# 再畫折線圖（前景）
for i, week in enumerate(pivot_df.columns):
    ax1.plot(x_values, pivot_df[week].values, marker="o", alpha=0.6, label=f"Week {week}", zorder=1)

# 設定第一個 y 軸
ax1.set_xlabel("ComC Weight")
ax1.set_ylabel("Soft Penalty")
ax1.grid(True, alpha=0.3)

# 設定 x 軸刻度，每 50 顯示一個標籤
x_ticks = np.arange(min(x_values), max(x_values) + 1, 50)
ax1.set_xticks(x_ticks)
ax1.set_xticklabels(x_ticks)

# 合併兩個圖例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

# 設定標題
plt.title(f"Soft Penalty vs ComC Weight for {scenario}")

# 調整圖表
plt.tight_layout()

# 儲存圖片
output_filename = f"soft_penalty_vs_comc_{scenario}_weight0_250.png"
plt.savefig(output_filename, dpi=300)
print(f"✅ 圖片已儲存為 {output_filename}")