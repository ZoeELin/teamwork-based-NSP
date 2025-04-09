import numpy as np
import matplotlib.pyplot as plt

# from scipy.optimize import minimize

# 設定參數
C0 = 60  # 初始合作成本
beta = 10  # 資深比例對成本的影響
gamma = 90  # 過高資深比例的影響

# 生成資深比例 r_s (從 0.1 到 0.9)
r_s_values = np.linspace(0.1, 0.9, 100)


# 成本函數 (U 型)
def cost_function(r_s):
    return C0 - beta * r_s + gamma * (r_s - 0.5) ** 2  # U 型函數


# 計算每個比例的合作成本
cost_values = np.array([cost_function(r) for r in r_s_values])

# 找出最佳 r_s (使 C(r_s) 最小)
optimal_r_s = r_s_values[np.argmin(cost_values)]
optimal_cost = np.min(cost_values)

# 繪製結果
plt.figure(figsize=(8, 5))
plt.plot(r_s_values, cost_values, label="Cooperation Cost Curve")
plt.axvline(
    optimal_r_s, color="r", linestyle="--", label=f"Optimal r_s = {optimal_r_s:.2f}"
)
plt.xlabel("Senior-to-Junior Ratio (r_s)")
plt.ylabel("Cooperation Cost")
plt.title("Finding Optimal Senior-to-Junior Ratio")
plt.legend()
plt.show()

# 顯示最佳比例
print(
    f"Optimal Senior-to-Junior Ratio: r_s* = {optimal_r_s:.2f}, Minimum Cost: {optimal_cost:.2f}"
)
