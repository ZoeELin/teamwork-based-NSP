import os
import time
import utils
import scheduler

from history import create_next_history_data


def run_scheduler_pipeline(instance, run_id="0"):
    """
    Performs a complete nurse scheduling process (using prepared instance dict).
    Includes weekly scheduling and results output with total execution time statistics.

    Parameters:
        instance (dict): scenario, scenario_name, week_data, history
    """
    output_dir = os.path.dirname(instance["scenario"])
    week_idx = 0
    his_filepath = instance["history"]

    start = time.perf_counter()

    print(
        f"Run scenario: {instance['scenario_name']}"
    )

    for week_data_file in instance["week_data"]:
        print(f"\nProcessing: week {week_idx}")
        print("=" * 80)

        final_assignments = scheduler.base_scheduler(
            instance["scenario"], week_data_file, his_filepath
        )

        utils.package_solution_2JSON(
            final_assignments, output_dir, instance["scenario_name"], week_idx, run_id
        )

        his_filepath = create_next_history_data(final_assignments, his_filepath)

        week_idx += 1

    end = time.perf_counter()
    print(f"\nExecution time: {end - start:.4f} seconds")
