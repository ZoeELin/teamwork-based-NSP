import re
from glob import glob

def parse_log_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    week_data = {}
    current_week = None
    execution_time = None

    for line in lines:
        # 找出目前是哪一週
        week_match = re.search(r'Processing: week (\d+)', line)
        if week_match:
            current_week = int(week_match.group(1))
            week_data[current_week] = {
                'Initial': {'Hard': 0, 'Soft': 0, 'ComC': 0, 'Total': 0},
                'Best': {'Hard': 0, 'Soft': 0, 'ComC': 0, 'Total': 0}
            }

        # 初始解的懲罰分數
        if 'Initial solution penalty' in line:
            match = re.search(r'penalties -- .*?H3: (\d+).*?S1: (\d+), S2\+S3\+S5: (\d+), S4: (\d+), ComC: ([\d\.]+)', lines[lines.index(line)-1])
            if match:
                h = int(match.group(1))
                s1 = int(match.group(2))
                s2s3s5 = int(match.group(3))
                s4 = int(match.group(4))
                comc = float(match.group(5))
                soft = s1 + s2s3s5 + s4
                total = h + soft + comc
                week_data[current_week]['Initial'] = {'Hard': h, 'Soft': soft, 'ComC': comc, 'Total': total}

        # 最佳解的總懲罰分
        if 'Best solution penalty' in line:
            match_total = re.search(r'Best solution penalty: ([\d\.]+)', line)
            if match_total:
                week_data[current_week]['Best']['Total'] = float(match_total.group(1))

        # 最佳解細項的 ComC（出現在最佳 solution penalty 前）
        if 'penalties --' in line and 'Best solution penalty' not in line:
            if 'H3: 0' in line:
                match = re.search(r'S1: (\d+), S2\+S3\+S5: (\d+), S4: (\d+), ComC: ([\d\.]+)', line)
                if match:
                    s1 = int(match.group(1))
                    s2s3s5 = int(match.group(2))
                    s4 = int(match.group(3))
                    comc = float(match.group(4))
                    soft = s1 + s2s3s5 + s4
                    week_data[current_week]['Best']['Hard'] = 0
                    week_data[current_week]['Best']['Soft'] = soft
                    week_data[current_week]['Best']['ComC'] = comc

        # Execution time
        if 'Execution time' in line:
            match_time = re.search(r'Execution time: ([\d\.]+) seconds', line)
            if match_time:
                execution_time = float(match_time.group(1))

    return week_data, execution_time

def print_summary_table(week_data, exec_time):
    print(f"{'':<8} {'':<20} {'Initial score':<15} {'Best score':<15}")
    for week in sorted(week_data.keys()):
        print(f"{'week'+str(week):<8}")
        for key in ['Hard', 'Soft', 'ComC', 'Total']:
            init_score = round(week_data[week]['Initial'][key], 2)
            best_score = round(week_data[week]['Best'][key], 2)
            print(f"{'':<8} {key + ' constraints':<20} {init_score:<15} {best_score:<15}")
        print()

    print(f"{'':<8} Execution time {exec_time:.2f} seconds")



def summarize_all_logs_to_file(input_dir, output_path="summary_output.txt"):
    files = sorted(glob(f"{input_dir}/scheduler_ComCw*_run12_*.txt"), key=lambda f: int(re.search(r'ComCw(\d+)', f).group(1)))
    with open(output_path, 'w') as out_file:
        for filename in files:
            comc_weight = re.search(r'ComCw(\d+)', filename)
            label = f"ComC weight: {comc_weight.group(1)}" if comc_weight else filename
            out_file.write(f"{label}\n")
            out_file.write(f"{'':<8} {'':<20} {'Initial score':<15} {'Best score':<15}\n")

            week_data, exec_time = parse_log_file(filename)
            print_summary_table(week_data, exec_time)

            # Write the summary to the output file
            for week in sorted(week_data.keys()):
                out_file.write(f"{'week'+str(week):<8}\n")
                for key in ['Hard', 'Soft', 'ComC', 'Total']:
                    init_score = round(week_data[week]['Initial'][key], 2)
                    best_score = round(week_data[week]['Best'][key], 2)
                    out_file.write(f"{'':<8} {key + ' constraints':<20} {init_score:<15} {best_score:<15}\n")
                out_file.write("\n")
            out_file.write(f"{'':<8} Execution time {exec_time:.2f} seconds\n")
            out_file.write("="*60 + "\n\n")

    print(f"✅ Summary written to {output_path}")


if __name__ == "__main__":
    summarize_all_logs_to_file("logs-weight50-50-1000/n030w4", "procession_with_n030w4_weight50_1000.txt")