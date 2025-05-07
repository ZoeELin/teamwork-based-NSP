import argparse
from instance_loader import select_instance_files


def parse_args():
    parser = argparse.ArgumentParser(
        description="NSP Solver Command-Line Interface", add_help=False
    )
    parser.add_argument(
        "--input_folder", required=True, help="Folder path, e.g., ./datasets"
    )
    parser.add_argument("--sce", required=True, help="Scenario name, e.g., n005w4")
    parser.add_argument(
        "--comc", type=int, default=0, help="Communication cost's weight (default: 0)"
    )
    parser.add_argument("--run_id", type=str, default="0", help="Run ID (default: 0)")
    parser.add_argument(
        "--output_dir", type=str, default="Output", help="Output folder (optional)"
    )

    # parser.add_argument(
    #     "--start-week",
    #     type=int,
    #     required=True,
    #     help="Start week (0~6 for 4 weeks, 0~2 for 8 weeks)",
    # )
    # parser.add_argument(
    #     "--history-index",
    #     type=int,
    #     choices=[0, 1, 2],
    #     required=True,
    #     help="Initial history index (0, 1, 2)",
    # )
    return parser.parse_args()


def cli_interface():
    args = parse_args()

    try:
        instance = select_instance_files(
            dataset_folder=args.dataset_folder,
            dataset_name=args.dataset_name,
            start_week=args.start_week,
            weeks_to_schedule=args.weeks_to_schedule,
            history_index=args.history_index,
        )

        print("\n✅ Successfully selected instance files:")
        print(f"📄 Scenario: {instance['scenario']}")
        print(f"📄 History: {instance['history']}")
        print(f"📄 Week Data:")
        for wd in instance["week_data"]:
            print("   -", wd)

    except Exception as e:
        print("⚠️ An error occurred:", e)

    return args
