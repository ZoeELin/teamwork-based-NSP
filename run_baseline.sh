#!/bin/bash

dataset_folder="./testdatasets_json"

output_dir="./Output_baseline_testdatasets"
comc_weight=0
logs="logs-baseline_testdatasets"

SCENARIOS=("n005w4" "n012w4" "n021w4")

for SCENARIO in "${SCENARIOS[@]}"

do
  echo "=== 開始處理 Scenario: $SCENARIO ==="
  scenario=$SCENARIO
  mkdir -p "${logs}/${scenario}"
  
  python3 Init_nurse_pairs.py "$dataset_folder/$scenario/Sc-$scenario.json" "${output_dir}/${scenario}"

  for i in {1..12}

  do
    timestamp=$(date +"%Y%m%d_%H%M%S")
    sol_dir="${output_dir}/${scenario}/Solutions-${i}"
    
    echo ">>> 第 $i 次執行 NSP 排班"
    python3 main.py \
      --input_folder "$dataset_folder" \
      --sce "$scenario" \
      --comc "$comc_weight" \
      --run_id "$i" \
      --output_dir "$output_dir" > "${logs}/${scenario}/scheduler_ComCw${comc_weight}_run${i}_${timestamp}.txt"

    
    echo ">>> 模擬合作圖（模擬第 $i 次後的結果）"
    python3 Simulate_coop.py "${output_dir}/${scenario}" "$sol_dir" "${i}" --comc "$comc_weight" > "${logs}/${scenario}/simulator-${i}th-coop_${i}_${timestamp}.txt"
  done
done