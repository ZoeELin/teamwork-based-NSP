import json
import os
import matplotlib.pyplot as plt
import pandas as pd


days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def visual_weekSchedule(filename):
    nurses = set()

    # 讀取 JSON 檔案
    with open(filename, "r") as f:
        data = json.load(f)

    # 取得護士與排班資訊
    assignments = data["assignments"]
    nurses.update(a["nurse"] for a in assignments)

    # 建立排班 DataFrame
    df = pd.DataFrame("", index=sorted(nurses), columns=days)
    for assign in assignments:
        df.loc[assign["nurse"], assign["day"]] = assign["shiftType"]


def visual_allWeekSchedule(folder):
    nurses = set()

    # 設定資料夾與 JSON 檔案名稱

    # 讀取該資料夾內的所有 .json 檔案
    json_files = [f for f in os.listdir(folder) if f.endswith(".json")]

    # 解析 JSON 數據
    schedule_data = {}

    for json_file in json_files:
        file_path = os.path.join(solution_folder, json_file)

        # 讀取 JSON 檔案
        with open(file_path, "r") as f:
            data = json.load(f)

        # 取得護士與排班資訊
        assignments = data["assignments"]
        nurses.update(a["nurse"] for a in assignments)

        # 建立排班 DataFrame
        df = pd.DataFrame("", index=sorted(nurses), columns=days)
        for assign in assignments:
            df.loc[assign["nurse"], assign["day"]] = assign["shiftType"]

        schedule_data[json_file] = df

    # 視覺化護士排班表
    fig, axes = plt.subplots(
        len(schedule_data), 1, figsize=(10, len(schedule_data) * 3)
    )

    for idx, (file_name, df) in enumerate(schedule_data.items()):
        ax = axes[idx] if len(schedule_data) > 1 else axes
        ax.axis("tight")
        ax.axis("off")
        table = ax.table(
            cellText=df.values,
            colLabels=df.columns,
            rowLabels=df.index,
            cellLoc="center",
            loc="center",
        )
        ax.set_title(file_name)

    plt.suptitle("Nurse Shift Schedules", fontsize=14)
    plt.show()


solution_folder = "testdatasets_json/n005w4/Solution_H_0-WD_1-2-3-3"
visual_allWeekSchedule(solution_folder)

# 儲存圖片
output_path = os.path.join(solution_folder, "nurse_shift_schedules.png")
plt.suptitle("Nurse Shift Schedules", fontsize=14)
plt.savefig(output_path, bbox_inches="tight")
plt.show()

print(f"排班表圖片已儲存至: {output_path}")
