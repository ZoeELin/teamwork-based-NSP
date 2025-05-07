#!/bin/bash

dataset_folder="./datasets_json"
output_dir="./Output_baseline-xx6"

comc_weight=0
logs="logs-baselinexx6"

# SCENARIOS=("n005w4" "n012w8" "n021w4")
SCENARIOS=("n030w4" "n030w8" "n040w4" "n040w8" "n050w4" "n050w8" "n060w4" "n060w8" "n080w4" "n080w8" "n100w4" "n100w8" "n120w4" "n120w8")

for SCENARIO in "${SCENARIOS[@]}"

do
  echo "=== 開始處理 Scenario: $SCENARIO ==="
  scenario=$SCENARIO
  mkdir -p "${logs}/${scenario}"

  timestamp=$(date +"%Y%m%d_%H%M%S")
  sol_dir="${output_dir}/${scenario}/Solutions-0"
    
  echo ">>> 執行 NSP 排班"
  python3 main.py \
    --input_folder "$dataset_folder" \
    --sce "$scenario" \
    --comc "$comc_weight" \
    --run_id 0 \
    --output_dir "$output_dir" > "${logs}/${scenario}/baselinexx6_scheduler${timestamp}.txt"

done