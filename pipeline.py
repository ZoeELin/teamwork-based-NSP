import os
import time


import utils
import scheduler


def run_scheduler_pipeline(instance):
    """
    Performs a complete nurse scheduling process (using prepared instance dict).
    Includes weekly scheduling and results output with total execution time statistics.

    Parameters:
        instance (dict): scenario, scenario_name, week_data, history
    """
    output_dir = os.path.dirname(instance["scenario"])
    week_idx = 0

    start = time.perf_counter()

    print(
        f".......................................{instance['scenario_name']}......................................."
    )

    for week_data in instance["week_data"]:
        print(f"\nProcessing: week {week_idx}")
        print("=" * 80)

        final_assignments = scheduler.supreme_scheduler(
            instance["scenario"], week_data, instance["history"]
        )

        utils.package_solution_2JSON(
            final_assignments, output_dir, instance["scenario_name"], week_idx
        )

        week_idx += 1

    end = time.perf_counter()
    print(f"\nExecution time: {end - start:.4f} seconds")
