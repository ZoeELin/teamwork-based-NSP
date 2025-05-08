import os
import re
from glob import glob

def extract_best_soft_penalty(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    best_total = None
    best_comc = None

    for i, line in enumerate(lines):
        if "Best solution penalty" in line:
            match = re.search(r'Best solution penalty: ([\d\.]+)', line)
            if match:
                best_total = float(match.group(1))

        if "penalties --" in line and "Best solution penalty" not in line:
            if 'H3: 0' in line:
                match = re.search(r'ComC: ([\d\.]+)', line)
                if match:
                    best_comc = float(match.group(1))

    if best_total is not None and best_comc is not None:
        return round(best_total - best_comc, 2)
    return None


def summarize_scenario_soft_penalties(root_dir, output_file="scenario_soft_summary.txt"):
    scenario_dirs = [d for d in sorted(os.listdir(root_dir)) if os.path.isdir(os.path.join(root_dir, d))]

    with open(output_file, "w") as f:
        f.write(f"{'Scenario':<20} {'Avg Soft Constraints':<25} {'Best Soft Constraints':<25}\n")
        f.write("=" * 70 + "\n")

        for scenario in scenario_dirs:
            scenario_path = os.path.join(root_dir, scenario)
            log_files = sorted(glob(os.path.join(scenario_path, "scheduler_ComCw500_run*.txt"))) # <--- Edit this to your logs files

            soft_penalties = []
            for log_file in log_files:
                penalty = extract_best_soft_penalty(log_file)
                if penalty is not None:
                    soft_penalties.append(penalty)

            if soft_penalties:
                avg_soft = round(sum(soft_penalties) / len(soft_penalties), 2)
                best_soft = round(min(soft_penalties), 2)
                f.write(f"{scenario:<20} {avg_soft:<25} {best_soft:<25}\n")
            else:
                f.write(f"{scenario:<20} {'N/A':<25} {'N/A':<25}\n")

    print(f"✅ Scenario soft constraint summary written to {output_file}")


if __name__ == "__main__":
    root_log_dir = "logs-weight50-50-1000"  # <--- Edit this to your logs directory
    summarize_scenario_soft_penalties(root_log_dir, "scenario_soft_summary_weight500.txt")