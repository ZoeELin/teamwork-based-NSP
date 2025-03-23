from pulp import LpProblem, LpVariable, LpMinimize, lpSum

# 建立問題
prob = LpProblem("Nurse_Scheduling", LpMinimize)

# 定義變數（假設有 x 名護士，y 個時段）
nurses = range(5)
shifts = range(10)
x = [[LpVariable(f"x_{n}_{s}", cat="Binary") for s in shifts] for n in nurses]

# 目標函數（最小化護士的總工作量偏差）
prob += lpSum(x[n][s] for n in nurses for s in shifts)

# 限制條件：確保每個時段至少有一名護士
for s in shifts:
    prob += lpSum(x[n][s] for n in nurses) >= 2

# 限制條件：每位護士最多只能被排 1 個班
for n in nurses:
    prob += lpSum(x[n][s] for s in shifts) <= 1

# 寫入 LP 檔案(檢查邏輯)
prob.writeLP("model.lp")
# 求解
prob.solve()
print("Optimal Schedule:")
for n in nurses:
    for s in shifts:
        if x[n][s].varValue == 1:
            print(f"Nurse {n} works shift {s}")
