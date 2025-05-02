import subprocess
import os

from instance_loader import select_instance_files


def run_validator(sce, his, weeks, sols, verbose=False, timeout=300):
    cmd = (
        ["java", "-jar", "tools/Validator.jar", "--sce", sce, "--his", his]
        + ["--weeks"]
        + weeks
        + ["--sols"]
        + sols
        + ["--out"]
        + ["results1.txt"]
    )
    if verbose:
        cmd.append("--verbose")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        print(result)
    except subprocess.TimeoutExpired:
        raise RuntimeError("Validator 超時，請檢查 timeout 設定")

    if result.returncode != 0:
        raise RuntimeError(f"Validator 執行失敗：{result.stderr}")

    # 解析並回傳標準輸出內容
    return result.stdout


input_folder = "testdatasets_json"
instance = select_instance_files(
    dataset_folder=input_folder,
    dataset_name="n021w4",
    start_week=0,
    history_index=0,
)

# 範例呼叫
sce_file = "testdatasets_json/n021w4/Sc-n021w4.json"
his_file = instance["history"]
week_files = instance["week_data"]

solutions_dir = "Output_testdatasets/n021w4/Solutions-12"
sol_files = sorted(
    [
        os.path.join(solutions_dir, f)
        for f in os.listdir(solutions_dir)
        if f.startswith("Sol-") and f.endswith(".json")
    ]
)

output = run_validator(sce_file, his_file, week_files, sol_files, verbose=True)
print(output)
