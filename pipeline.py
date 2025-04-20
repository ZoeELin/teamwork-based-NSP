import os
import time
import utils
import scheduler

from history import create_next_history_data


def run_scheduler_pipeline(instance, input_file, output_file, comc_w=0, run_id="0"):
    """
    Performs a complete nurse scheduling process (using prepared instance dict).
    Includes weekly scheduling and results output with total execution time statistics.

    Parameters:
        instance (dict): scenario, scenario_name, week_data, history
    """
    week_idx = 0
    history_filepath = instance["history"]

    start = time.perf_counter()

    print(f"Run scenario: {instance['scenario_name']}")

    for week_data_file in instance["week_data"]:
        print(f"\nProcessing: week {week_idx}")
        print("=" * 80)

        sol_path = f"{output_file}-{int(run_id)}"

        final_assignments = scheduler.base_scheduler(
            instance["scenario"], week_data_file, history_filepath, run_id
        )

        utils.package_solution_2JSON(
            final_assignments,
            sol_path,
            instance["scenario_name"],
            week_idx,
            run_id,
            comc_w,
        )

        history_filepath = create_next_history_data(
            final_assignments, history_filepath, sol_path
        )
        week_idx += 1

    end = time.perf_counter()
    print(f"\nExecution time: {end - start:.4f} seconds")
