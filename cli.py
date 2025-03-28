from instance_loader import select_instance_files


def cli_interface():
    print("🧠 INRC-II Instance Selector CLI")
    dataset_folder = input("請輸入資料夾路徑，例如 ./datasets/n005w4 ：").strip()
    dataset_name = input("請輸入 dataset 名稱（如 n005w4）：").strip()
    weeks_to_schedule = int(input("請輸入要排的週數（4 或 8）："))

    max_start_week = 10 - weeks_to_schedule
    print(f"👉 可選的起始週：0 ~ {max_start_week}")
    start_week = int(input(f"請輸入起始週（0~{max_start_week}）："))

    history_index = int(input("請選擇初始 history 編號（0、1、2）："))

    try:
        instance = select_instance_files(
            dataset_folder=dataset_folder,
            dataset_name=dataset_name,
            start_week=start_week,
            weeks_to_schedule=weeks_to_schedule,
            history_index=history_index,
        )

        print("\n✅ 已成功選擇 instance 檔案：")
        print(f"📄 Scenario: {instance['scenario']}")
        print(f"📄 History: {instance['history']}")
        print(f"📄 Week Data:")
        for wd in instance["week_data"]:
            print("   -", wd)

    except Exception as e:
        print("⚠️ 發生錯誤：", e)


# cli_interface()
