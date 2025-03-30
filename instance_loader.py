import os


def select_instance_files(
    dataset_folder: str,
    dataset_name: str,
    start_week: int = 0,
    history_index: int = 0,
):
    """
    A set of instance required files is automatically organized,
    based on the starting week and the number of scheduled weeks
    Args:
        dataset_folder (str): dataset file path
        dataset_name (str): scenario
        start_week (int): e.g., 0~6(w4) or 0~2(w8)
        history_index (int): 0~2

    Returns:
        dict: including scenario, history, week_data list
    """
    scenario_folder = f"{dataset_folder}/{dataset_name}"
    scenario_file = f"Sc-{dataset_name}.json"
    history_file = f"H0-{dataset_name}-{history_index}.json"
    weeks_to_schedule = int(dataset_name[-1])
    week_data_files = [
        f"WD-{dataset_name}-{w}.json"
        for w in range(start_week, start_week + weeks_to_schedule)
    ]

    # Confirm whether the file exist
    all_files = [scenario_file, history_file] + week_data_files
    missing = [
        f for f in all_files if not os.path.exists(os.path.join(scenario_folder, f))
    ]
    if missing:
        raise FileNotFoundError(f"❌ 找不到下列檔案：{missing}")

    return {
        "scenario_name": dataset_name,
        "scenario": os.path.join(scenario_folder, scenario_file),
        "history": os.path.join(scenario_folder, history_file),
        "week_data": [os.path.join(scenario_folder, f) for f in week_data_files],
    }
