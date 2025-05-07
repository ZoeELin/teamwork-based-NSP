import os


def select_instance_files(
    dataset_folder: str,
    dataset_name: str,
    start_week: int = 0,
    history_index: int = 0,
):
    """
    Automatically selects and verifies the required files for a scheduling instance,
    based on the starting week and the number of scheduled weeks
    Args:
        dataset_folder (str): Root directory containing the dataset.
        dataset_name (str): Name of the dataset, e.g., n005w4
        start_week (int): Starting week index for scheduling (e.g., 0–6 if scheduling 4 weeks).
        history_index (int): Index of the historical file to use (e.g., 0–2).

    Returns:
        dict: A dictionary containing:
            - 'scenario_name': The name of the dataset.
            - 'scenario': Full path to the scenario file.
            - 'history': Full path to the history file.
            - 'week_data': A list of full paths to the weekly data files.
    """
    scenario_folder = os.path.join(dataset_folder, dataset_name)
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
    if not os.path.exists(scenario_folder):
        raise FileNotFoundError(f"❌ Cannot find the dataset folder: {dataset_folder}")

    if missing:
        raise FileNotFoundError(f"❌ Cannot find these files: {missing}")

    return {
        "scenario_name": dataset_name,
        "scenario": os.path.join(scenario_folder, scenario_file),
        "history": os.path.join(scenario_folder, history_file),
        "week_data": [os.path.join(scenario_folder, f) for f in week_data_files],
    }
