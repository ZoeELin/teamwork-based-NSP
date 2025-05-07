import re
import matplotlib.pyplot as plt
import pandas as pd

filepath = "extracted/soft_penalty_summary_n021w4.txt"


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

# 繪圖
plt.figure(figsize=(12, 6))
pivot_df.plot(marker="o")
plt.title("Soft Penalty vs ComC Weight")
plt.xlabel("ComC Weight")
plt.ylabel("Soft Penalty")
plt.grid(True)
plt.legend(title="Week")
plt.tight_layout()
# plt.show()

# 儲存圖片
output_filename = "soft_penalty_vs_comc.png"
plt.savefig(output_filename, dpi=300)
print(f"✅ 圖片已儲存為 {output_filename}")