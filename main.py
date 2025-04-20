import time
import instance_loader
import pipeline
import scheduler
import sys
from cli import cli_interface


def main():
    run_id = sys.argv[1] if len(sys.argv) > 1 else "0"  # 預設 run_id 為 0
    scenario_name = "n021w4"
    instance = instance_loader.select_instance_files("testdatasets_json", scenario_name)

    # args = cli_interface()  # Parse arguments using cli_interface
    # instance = instance_loader.select_instance_files(
    #     dataset_folder=args.dataset_folder,
    #     dataset_name=args.dataset_name,
    #     start_week=args.start_week,
    #     weeks_to_schedule=args.weeks_to_schedule,
    #     history_index=args.history_index,
    # )
    input_file = f"testdatasets_json/{scenario_name}"
    output_path = f"Output/{scenario_name}/Solutions"
    comc_weight = 0
    pipeline.run_scheduler_pipeline(
        instance, input_file, output_path, comc_weight, run_id
    )


def test_one_week():
    sce_path = "datasets_json/n030w4/Sc-n030w4.json"
    weekdata_path = "datasets_json/n030w4/WD-n030w4-0.json"
    history_path = "datasets_json/n030w4/H0-n030w4-0.json"
    start = time.perf_counter()
    scheduler.supreme_scheduler(sce_path, weekdata_path, history_path)
    end = time.perf_counter()
    print(f"\nExecution time: {end - start:.4f} seconds")


if __name__ == "__main__":
    main()
