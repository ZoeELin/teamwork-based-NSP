from collections import defaultdict
import pandas as pd

import instance_loader
import pipeline
import scheduler


def main():
    instance = instance_loader.select_instance_files("testdatasets_json", "n005w4")
    pipeline.run_scheduler_pipeline(instance)


def test_one_week():
    sce_path = "testdatasets_json/n005w4/Sc-n005w4.json"
    weekdata_path = "testdatasets_json/n005w4/WD-n005w4-0.json"
    history_path = "testdatasets_json/n005w4/H0-n005w4-0.json"
    scheduler.supreme_scheduler(sce_path, weekdata_path, history_path)


if __name__ == "__main__":
    main()
