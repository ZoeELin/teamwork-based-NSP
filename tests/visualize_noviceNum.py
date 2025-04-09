import matplotlib.pyplot as plt
import numpy as np

# Assuming time cost increases linearly with the number of novices
novices_range = np.arange(0, 11)
base_time_cost = 10  # Base cost with 1 novice
increment_per_novice = 5  # Incremental cost per additional novice
# Calculating time costs for 0 to 10 novices
time_costs_linear = base_time_cost + increment_per_novice * (novices_range - 1)


# Parameters for the simulation using logarithmic and square root functions

a_log = 10  # 調節對數函數增長的速率或幅度
b_log = 2  # 縮放因子（值增加即使只增加少量新人，時間成本也會顯著增加）
c_log = 5  # 没有新人時的初始或基本時間成本

a_sqrt = 12  # Scale factor for the square root model
c_sqrt = 5  # 没有新人時（或者說是在新人數量最小時）的初始或基本時間成本


# Calculating time costs using logarithmic and square root functions
time_costs_log = a_log * np.log(b_log * novices_range + 1) + c_log
time_costs_sqrt = a_sqrt * np.sqrt(novices_range) + c_sqrt

# Plotting the data
plt.figure(figsize=(12, 8))
plt.plot(
    novices_range,
    time_costs_linear,
    marker="o",
    linestyle="--",
    color="purple",
    label="Linear Model",
)

plt.plot(
    novices_range,
    time_costs_log,
    marker="o",
    linestyle="-",
    color="blue",
    label="Logarithmic Model",
)
plt.plot(
    novices_range,
    time_costs_sqrt,
    marker="o",
    linestyle="--",
    color="green",
    label="Square Root Model",
)
plt.title("Time Cost vs. Number of Novices in Team")
plt.xlabel("Number of Novices")
plt.ylabel("Time Cost(minutes)")
plt.legend()
plt.grid(True)
plt.show()
