import random
import math

# 護士與班次
nurses = ["A", "B", "C"]
shifts = list(range(5))  # 5 個班次
temperature = 100  # 初始溫度
cooling_rate = 0.95  # 降溫速率
min_temperature = 1e-3  # 終止條件


# 隨機生成初始解
def random_schedule():
    return {shift: random.choice(nurses) for shift in shifts}


# 計算成本函數（護士之間的班次不均衡程度）
def cost(schedule):
    workload = {nurse: 0 for nurse in nurses}
    for shift in schedule.values():
        workload[shift] += 1
    variance = sum(
        (workload[n] - len(shifts) / len(nurses)) ** 2 for n in nurses
    )  # 計算方差
    return variance  # 越小越均衡


# **正確的鄰近解生成方式**（僅改變一個班次的護士）
def generate_neighbor(schedule):
    new_schedule = schedule.copy()
    shift_to_change = random.choice(shifts)  # 隨機選擇一個班次
    new_nurse = random.choice(nurses)  # 隨機選擇一個護士
    new_schedule[shift_to_change] = new_nurse  # 變更班次護士
    return new_schedule


# **模擬退火演算法**
def simulated_annealing():
    current_solution = random_schedule()
    current_cost = cost(current_solution)
    temp = temperature

    while temp > min_temperature:
        new_solution = generate_neighbor(current_solution)  # 產生鄰近解
        new_cost = cost(new_solution)
        delta = new_cost - current_cost

        # 如果新解更好，接受它；如果更差，則根據機率決定是否接受
        if delta < 0 or random.uniform(0, 1) < math.exp(-delta / temp):
            current_solution, current_cost = new_solution, new_cost

        temp *= cooling_rate  # 降溫

    return current_solution


# **執行模擬退火**
best_schedule = simulated_annealing()
print("最佳排班結果:", best_schedule)
