# Nurse Scheduling Problem
This project implements a nurse scheduling problem.
---

## Overview

The scheduling process consists of three main steps:
1. **Generate an initial schedule** considering cooperation cost.
2. **Initialize nurse pairs** to prepare for cooperation calculations.
3. **Simulate cooperation** and calculate cooperation intensity scores.

---

## Tutorial

### Step 1: Start Scheduling

Use `main.py` to generate the schedule.

```bash
python3 main.py \
    --input_folder <dataset_folder> \
    --sce <scenario_name> \
    --comc <communication cost weight> \
    --run_id <i-th time of run d> \
    --output_dir <output_directory>
```

e.g. 
```
python3 main.py --input_folder ./testdatasets_json --sce n005w4 --comc 200 --run_id 0 --output_dir ./Output_test

python3 main.py --input_folder ./testdatasets_json --sce n021w4 --comc 200 --run_id 0 --output_dir ./Output

python3 main.py --input_folder ./Data/datasets_json --sce n030w4 --comc 0 --run_id 0 --output_dir ./Output_test0509
```
Arguments:
- <dataset_folder>: Path to the dataset folder.
- <scenario_name>: Scenario name (e.g., n005w4).
- <comc_weight>: Cooperation cost weight (e.g., 200).
- <run_id>: Run ID (integer, e.g., 0).
- <output_dir>: Path to the output directory for storing results.


### Step 2: Initial every nurses' pairs
Run Init_nurse_pairs.py to set up initial nurse pair data needed for cooperation calculations.
```
python3 Init_nurse_pairs.py <sce_file> <output_directory>
```
Example: 
```
python3 Init_nurse_pairs.py datasets_json/n030w4/Sc-n030w4.json Output_dataset/n030w4
```
Arguments:
- <scenario_file>: Path to the scenario JSON file.
- <output_directory>: Directory to save the initialized nurse pair data.


### Step 3: Calculate cooperation intensity
Run Simulate_coop.py to calculate cooperation intensity scores based on the generated schedules.
```
python3 Simulate_coop.py <scenario_output_dir> <solution_dir> <run_id> [--comc <comc_weight>]
```

Example without specifying --comc (default value will be used):
```
python3 Simulate_coop.py ./Output_test/n005w4 Output_test/n005w4/Solutions-ComC200-0 1
```
Example with specifying --comc:
```
python3 Simulate_coop.py ./Output_test/n005w4 Output_test/n005w4/Solutions-ComC200-0 1 --comc 200
```
Arguments:
- <scenario_output_dir>: Path to the output directory of the scenario (e.g., ./Output_test/n005w4).
- <solution_dir>: Path to the directory containing generated solutions.
- <run_id>: Run ID used during scheduling.
- --comc (optional): Cooperation cost weight. Must match the weight used in Step 1 if specified.

---
## Notes
