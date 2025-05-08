import re
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import math

# 設定全域變數
cmap = cm.get_cmap('tab10')  # 最多支援10個不同顏色（超過也會重複）

# 計算溫度變化的迭代次數
def calculate_temp_iterations(init_temp, min_temp, cooling_rate, max_iteration=2*10**4):
    iteration = 0
    iters = [iteration]
    temps = [init_temp]
    current_temp = init_temp
    k = int(math.log(min_temp/init_temp) / math.log(cooling_rate))  # 轉換為整數
    inner_iter = max_iteration // k

    for i in range(k):
        iteration += inner_iter
        iters.append(iteration)
        temps.append(current_temp * cooling_rate)
        current_temp = temps[-1]

    return iters, temps

# 儲存每週的溫度與懲罰值
week_data = {}  # e.g., {0: [(temp1, penalty1), (temp2, penalty2)], 1: [...], ...}
week_iterations = {}  # e.g., {0: [penalty1, penalty2], 1: [penalty3, penalty4], ...}

current_week = None
current_temp = None

def parse_log_file(file_path):

    # Read and parse log
    with open(file_path, "r") as f:
        for line in f:
            # Check if switch to new week
            week_match = re.search(r'Processing: week (\d+)', line)
            if week_match:
                current_week = int(week_match.group(1))
                if current_week not in week_data:
                    week_data[current_week] = []
                    week_iterations[current_week] = []

            # Get current temperature and penalty
            temp_match = re.search(r'> Current temperature: ([\d\.]+), current penalties: (\d+)', line)
            if temp_match:
                current_temp = float(temp_match.group(1))
                current_penalty = int(temp_match.group(2)) 
                week_data[current_week].append((current_temp, current_penalty))

            # Get neighbor penalty(2 * 10000 times)
            neighbor_penalty_match = re.search(r'penalties (\d+)', line)
            if neighbor_penalty_match:
                neighbor_penalty = int(neighbor_penalty_match.group(1))
                week_iterations[current_week].append(neighbor_penalty)

        # neighbor = []
        # if neighbor_penalty_match and current_temp is not None and current_week is not None:
        #     penalties = int(neighbor_penalty_match.group(1))
        #     neighbor.append(penalties)
    return week_data, week_iterations


def plot_temperature_vs_penalty(week_data, scenario):
    plt.figure(figsize=(30, 7))

    all_temperatures = set()
    

    for i, (week, data) in enumerate(sorted(week_data.items())):
        temps, pens = zip(*data)
        all_temperatures.update(temps)
        plt.plot(
            temps,
            pens,
            marker='o',
            markersize=3,         # 點變小
            linewidth=1,          # 線條細
            alpha=0.5,            # 半透明線
            label=f"Week {week}",
            color=cmap(i % 10)
        )

    # 加上垂直線在每個 temperature 上
    for t in sorted(all_temperatures):
        plt.axvline(x=t, color='gray', linewidth=0.5, alpha=0.8)  # 垂直線

    # 設定 x 軸刻度標籤
    sorted_temps = sorted(all_temperatures, reverse=True)  # 從大到小排序
    plt.xticks(sorted_temps, [f"{temp:.1f} (level {i+1})" for i, temp in enumerate(sorted_temps)], rotation=90, fontsize=6)
    # 圖表格式
    plt.xlabel("Temperature")
    plt.ylabel("Penalty")
    plt.title(f"Temperature vs Penalty for Each Week during Simulated Annealing in {scenario}")
    plt.grid(True, alpha=0.1)
    plt.gca().invert_xaxis()
    plt.legend(title="Week")
    plt.tight_layout()

    # 儲存與顯示
    filename = f"temperature_vs_penalty_per_week-{scenario}-comc100.png"
    plt.savefig(filename, dpi=300)
    print(f"✅ Saved to {filename}")
    plt.show()

def plot_penalty_vs_iterations(week_iterations, scenario):
    plt.figure(figsize=(30, 7))

    
    # 顏色配置
    cmap = cm.get_cmap('tab10')  # 最多支援10個不同顏色（超過也會重複）
    for i, (week, penalties_list) in enumerate(sorted(week_iterations.items())):
        iterations = list(range(1, len(penalties_list) + 1))
        
        plt.scatter(
            iterations,
            penalties_list,
            s=2,              # 點的大小
            alpha=0.5,        # 半透明
            label=f"Week {week}",
            color=cmap(i % 10)
        )
    
        # 加入垂直線標示溫度變化   
        # 計算溫度變化的迭代次數
        iterations, temp_iterations = calculate_temp_iterations(110, 2.13, 0.95)
        for idx, iter_point in enumerate(iterations):
            plt.axvline(x=iter_point, color='black', linewidth=0.5, alpha=1)
        
    
    # 設定 x 軸刻度標籤
    plt.xticks(iterations, [f"Level {i+1}\n{iter}" for i, iter in enumerate(iterations)], rotation=90)

    # 圖表格式
    plt.xlabel("Iterations")
    plt.ylabel("Penalty")
    plt.title("Penalty vs Iterations for Each Week")
    plt.grid(True, alpha=0.3)
    plt.legend(title="Week")
    plt.tight_layout()

    # 儲存與顯示
    filename = f"iterations_vs_penalty_per_week-{scenario}-comc100.png"
    plt.savefig(filename, dpi=300)
    print(f"✅ Saved to {filename}")
    plt.show()

def main():
    log_file = 'logs-comc100_0508/n030w4/scheduler_ComCw100_run2_20250508_073350.txt'
    scenario = "n030w4"
    temp_data, iter_data = parse_log_file(log_file)
    
    # 畫溫度vs懲罰值的圖
    plot_temperature_vs_penalty(temp_data, scenario)
    
    # 畫迭代次數vs懲罰值的圖
    plot_penalty_vs_iterations(iter_data, scenario)


if __name__ == "__main__":
    main() 