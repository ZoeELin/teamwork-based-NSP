import os
import re
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
from statistics import mean
from collections import defaultdict


# 萃取單一 log 檔中每週的 soft penalty（S1 + S2+S3+S5 + S4）
def extract_soft_penalties_per_week(file_path):
    with open(file_path, "r") as f:
        content = f.read()

    # 每週以 "Processing: week X" 為界分割
    week_blocks = re.split(r"Processing: week \d+", content)[1:]

    soft_penalties = []
    for block in week_blocks:
        soft_values = re.findall(
            r"S1:\s*([\d\.]+),\s*S2\+S3\+S5:\s*([\d\.]+),\s*S4:\s*([\d\.]+)", block)
        if not soft_values:
            continue
        last_s1, last_s23s5, last_s4 = soft_values[-1]
        soft_penalty = float(last_s1) + float(last_s23s5) + float(last_s4)
        soft_penalties.append(round(soft_penalty, 2))

    return soft_penalties


# 每個 scenario、每個 ComC weight、每週的所有 run 的 soft penalties（保留所有值）
def collect_scenario_all_soft_penalties_and_best_soft_penalty(root_dir):
    scenario_dirs = sorted([d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))])
    scenario_data_all = {}
    scenario_data_best = {}

    for scenario in scenario_dirs:
        scenario_path = os.path.join(root_dir, scenario)
        log_files = glob(os.path.join(scenario_path, "scheduler_ComCw*_run*.txt"))

        weight_week_penalties = defaultdict(list)
        best_penalty = float("inf")

        for log_file in log_files:
            match = re.search(r'ComCw(\d+)', log_file)
            if not match:
                continue
            weight = int(match.group(1))
            week_penalties = extract_soft_penalties_per_week(log_file)
            best_penalty = min(min(week_penalties), best_penalty)
            instance_penalty = sum(week_penalties) / len(week_penalties)

            weight_week_penalties[weight].append(instance_penalty)

        scenario_data_all[scenario] = weight_week_penalties
        scenario_data_best[scenario] = best_penalty

    return scenario_data_all, scenario_data_best


# 繪製 bar chart：每個 weight 下，每個 scenario 的最小 soft constraints
def plot_bar_chart(scenario_data, output_img="bar_chart_best_soft.png"):
    scenarios = list(scenario_data.keys())
    best_values = list(scenario_data.values())
    x = np.arange(len(scenarios))

    plt.figure(figsize=(12, 6))
    bars = plt.bar(x, best_values, color='skyblue')

    plt.xlabel("Scenario")
    plt.ylabel("Best Soft Constraint Penalty")
    plt.title("Best Soft Constraints per Scenario")
    plt.xticks(x, scenarios, rotation=45)
    plt.grid(axis="y")

    # 顯示數值標籤在 bar 上方
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 20, f'{height:.0f}', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_img, dpi=300, bbox_inches="tight")
    plt.show()

    print(f"✅ Bar chart saved to {output_img}")


# 繪製 line chart：每個 scenario 一條線，顯示每個 weight 下的平均 soft constraints（12 run 平均）
def plot_avg_soft_constraints_by_scenario(scenario_data_all_runs, output_img="avg_soft_constraints_per_scenario.png"):
    plt.figure(figsize=(14, 6))
    all_weights = sorted({w for s in scenario_data_all_runs.values() for w in s})

    for scenario, weight_dict in scenario_data_all_runs.items():
        avg_softs = []
        for w in all_weights:
            if w in weight_dict:
                avg = np.mean(weight_dict[w])  # 計算此 scenario 該權重的平均值（12 runs）
            else:
                avg = np.nan  # 若該權重沒有值，避免報錯，設為 NaN
            avg_softs.append(avg)

        plt.plot(all_weights, avg_softs, marker='o', label=scenario)


    plt.xlabel("ComC Weight")
    plt.ylabel("Average Soft Constraints (run1 ~ run12)")
    plt.title("Average Soft Constraints by Scenario (per Weight)")
    plt.grid(True)
    plt.legend()
    plt.legend(bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(output_img)
    plt.show()
    print(f"✅ Average scenario soft constraints plot saved to {output_img}")


def plot_combined_chart(scenario_best_data, scenario_all_runs_data, output_img="combined_soft_constraints_plot.png"):
    plt.figure(figsize=(14, 7))

    all_weights = sorted({w for s in scenario_best_data.values() for w in s})
    scenarios = list(scenario_best_data.keys())
    x = np.arange(len(all_weights))
    bar_width = 0.8 / len(scenarios)

    # 畫 Bar：Best Soft Constraints
    for idx, scenario in enumerate(scenarios):
        best_y = [scenario_best_data[scenario].get(w, np.nan) for w in all_weights]
        offset = x + idx * bar_width - (len(scenarios) / 2) * bar_width + bar_width / 2
        plt.bar(offset, best_y, width=bar_width, alpha=0.5, label=f"{scenario} (Best)")

    # 畫 Line：Average Soft Constraints
    for scenario, weight_dict in scenario_all_runs_data.items():
        avg_softs = [np.mean(weight_dict[w]) if w in weight_dict else np.nan for w in all_weights]
        plt.plot(x, avg_softs, marker='o', linestyle='-', label=f"{scenario} (Avg)")

    plt.xlabel("ComC Weight")
    plt.ylabel("Soft Constraints")
    plt.title("Best and Average Soft Constraints by Scenario")
    plt.xticks(x, all_weights)
    plt.grid(True)
    plt.legend()
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.savefig(output_img)
    plt.show()

    print(f"✅ Combined chart saved to {output_img}")


if __name__ == "__main__":
    root_log_dir = "logs-weight0-50-1000"  # ✅ 修改為你的 logs 根目錄資料夾

    scenario_all_data, scenario_best_data = collect_scenario_all_soft_penalties_and_best_soft_penalty(root_log_dir)
    # print(scenario_all_data)
    # print(scenario_best_data)
    
    # 圖 1：bar chart - 每個 weight、每個 scenario 的最佳值
    plot_bar_chart(scenario_best_data, "bar_chart_best_soft.png")

    # 圖 2：line chart - 每個 scenario 的平均 soft constraints（12 run 平均）
    plot_avg_soft_constraints_by_scenario(scenario_all_data, "avg_soft_constraints_per_scenario.png")

    # # 圖 3：combined chart - 每個 weight 下的最佳值和平均值
    # plot_combined_chart(scenario_best_data, scenario_all_data, "combined_soft_constraints_plot.png")