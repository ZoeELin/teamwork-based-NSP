# 學長的程式碼，用來計算護士之間的團隊合作成本


import numpy as np

# 設定排班數據
R = 5  # 醫院病房數
D = 30  # 排班天數
W = 4  # 週數
N = 10  # 總共 10 名護士

# 初始化 T 矩陣，記錄護士 p, q 之間的合作次數
T = np.zeros((N, N))

# 模擬歷史合作數據 (假設隨機分配護士到病房)
np.random.seed(42)  # 固定亂數種子
for _ in range(100):  # 模擬 100 次排班數據
    nurse_team = np.random.choice(N, size=3, replace=False)  # 隨機選 3 名護士一起工作
    for i in range(3):
        for j in range(i + 1, 3):
            T[nurse_team[i], nurse_team[j]] += 1
            T[nurse_team[j], nurse_team[i]] += 1  # 對稱矩陣

# 計算團隊合作成本
teamwork_cost = np.ones((N, N)) - (T / (R * D * W))

# 輸出部分結果
print("護士合作次數矩陣 T：")
print(T)

print("\n護士之間的團隊合作成本 (c_pq)：")
print(teamwork_cost)
