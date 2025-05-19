import os
import re
import matplotlib.pyplot as plt


log_folder = "logs-datasets0515_0-250/n030w4"
scenario = "n030w4-0-250"
output_img_file = f"scheduler_score_vs_comc_{scenario}.png"

data_points = []

def parse_fianl_penalty(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    pending_best_penalty_line = None
    soft_score_list = []
    comc_list = []
    for line in lines:
        if 'penalties ' in line:
            pending_best_penalty_line = line

        # 最佳解的總懲罰分
        if 'Best solution penalty' in line:
            match_best_solution = re.search(r'Best solution penalty: ([\d\.]+)', line)
            if match_best_solution:
                if pending_best_penalty_line:
                    match = re.search(
                        r'S1: (\d+), S2\+S3\+S5: (\d+), S4: (\d+), ComC: ([\d\.]+)',
                        pending_best_penalty_line
                    )
                    if match:
                        s1 = int(match.group(1))
                        s2s3s5 = int(match.group(2))
                        s4 = int(match.group(3))
                        comc = float(match.group(4))

                        soft = s1 + s2s3s5 + s4
                        soft_score_list.append(soft)
                        comc_list.append(comc)

    return soft_score_list, comc_list 



for filename in os.listdir(log_folder):
    if not filename.startswith("scheduler_ComCw"):
        continue

    comc_match = re.search(r"ComCw(\d+)", filename)
    if not comc_match:
        continue
    comc_weight = int(comc_match.group(1))

    file_path = os.path.join(log_folder, filename)
    print(file_path)
    soft_score, comc_list = parse_fianl_penalty(file_path)
    data_points.extend((comc_weight, comc, soft) for comc, soft in zip(comc_list, soft_score))

# 分組著色
colors = {}
for cw, _, _ in data_points:
    if cw not in colors:
        colors[cw] = f"C{len(colors)}"

# 畫圖
plt.figure(figsize=(30, 12))
for cw, comc, soft_score in data_points:
    plt.scatter(comc, soft_score, color=colors[cw], alpha=0.6, label=f"ComCw {cw}")

# 去除重複 legend
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(1.05, 1), loc="upper left")

plt.xlabel("ComC Weight")
plt.ylabel("Soft Constraint Score")
plt.title("Soft Constraints vs ComC Weight")
plt.grid(True)
plt.tight_layout()
plt.show()

plt.savefig(output_img_file)
print(f"✅ Saved to {output_img_file}")