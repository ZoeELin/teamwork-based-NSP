import time
import instance_loader
import pipeline
import scheduler
from cli import cli_interface


def main():
    instance = instance_loader.select_instance_files("testdatasets_json", "n005w4")

    # args = cli_interface()  # Parse arguments using cli_interface
    # instance = instance_loader.select_instance_files(
    #     dataset_folder=args.dataset_folder,
    #     dataset_name=args.dataset_name,
    #     start_week=args.start_week,
    #     weeks_to_schedule=args.weeks_to_schedule,
    #     history_index=args.history_index,
    # )
    pipeline.run_scheduler_pipeline(instance)


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
