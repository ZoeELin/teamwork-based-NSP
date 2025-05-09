import os
import time
import utils
import scheduler

from history import create_next_history_data


def run_scheduler_pipeline(instance, output_dir, comc_w, run_id_str):
    """
    Performs a complete nurse scheduling process (using prepared instance dict).
    Includes weekly scheduling and results output with total execution time statistics.

    Parameters:
        instance (dict): scenario, scenario_name, week_data, history
    """
    scenario_dir = os.path.join(output_dir, instance["scenario_name"])

    if comc_w == 0:
        solution_dir = os.path.join(
        output_dir, instance["scenario_name"], f"Solutions-{run_id_str}"
    )
    else:
        solution_dir = os.path.join(
            output_dir,
            instance["scenario_name"],
            f"Solutions-ComC{comc_w}-{run_id_str}",
        )

    week_idx = 0
    history_filepath = instance["history"]

    start = time.perf_counter()

    print(f"Run scenario: {instance['scenario_name']}")

    for week_data_file in instance["week_data"]:
        print(f"\nProcessing: week {week_idx}")
        print("=" * 80)

        final_assignments = scheduler.mcts_scheduler(
            instance["scenario"],
            week_data_file,
            scenario_dir,
            history_filepath,
            int(run_id_str),
            comc_w,
        )

        utils.package_solution_2JSON(
            final_assignments,
            solution_dir,
            instance["scenario_name"],
            week_idx,
        )

        history_filepath = create_next_history_data(
            final_assignments, history_filepath, solution_dir
        )
        week_idx += 1

    end = time.perf_counter()
    print(f"\nExecution time: {end - start:.4f} seconds")
