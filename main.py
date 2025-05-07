import time
import instance_loader
import pipeline
import scheduler
import sys
import cli
import os


def main():
    args = cli.parse_args()

    scenario_name = args.sce
    run_id = args.run_id
    comc_weight = int(args.comc)
    dataset_dir = args.input_folder
    output_dir = args.output_dir

    instance = instance_loader.select_instance_files(dataset_dir, scenario_name)

    pipeline.run_scheduler_pipeline(instance, output_dir, comc_weight, run_id)


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
