#!/bin/bash

dataset_folder="./Data/datasets_json"

output_dir="./Output_datasets0515_0-250"
comc_weight=0
logs="logs-datasets0515_0-250"

SCENARIOS=("n030w4" "n040w4" "n050w4" "n060w4" "n080w4" "n100w4" "n120w4")
# SCENARIOS=("n050w4" "n030w8" "n040w8" "n050w8"  "n060w8" "n080w8" "n100w8" "n120w8")

for SCENARIO in "${SCENARIOS[@]}"
do

  echo "=== 開始處理 Scenario: $SCENARIO ==="
  scenario=$SCENARIO
  mkdir -p "${logs}/${scenario}"

  for comc_weight in $(seq 0 5 250)
  do
    
    echo ">ComC weight: ${comc_weight}"
    python3 Init_nurse_pairs.py "$dataset_folder/$scenario/Sc-$scenario.json" "${output_dir}/${scenario}"
    
    for i in $(seq 1 12)
    do

      timestamp=$(date +"%Y%m%d_%H%M%S")
      if [ "$comc_weight" -eq 0 ]; then
          sol_dir="${output_dir}/${scenario}/Solutions-${i}"
      else
          sol_dir="${output_dir}/${scenario}/Solutions-ComC${comc_weight}-${i}"
      fi
      
      echo ">>> 第 $i 次執行 NSP 排班"
      python3 main.py \
        --input_folder "$dataset_folder" \
        --sce "$scenario" \
        --comc "$comc_weight" \
        --run_id "$i" \
        --output_dir "$output_dir" > "${logs}/${scenario}/scheduler_ComCw${comc_weight}_run${i}_${timestamp}.txt"

      
      echo ">>> 模擬合作圖（模擬第 $i 次後的結果）"
      python3 Simulate_coop.py "${output_dir}/${scenario}" "$sol_dir" "${i}" --comc "$comc_weight" > "${logs}/${scenario}/simulator-${i}th-coop_${comc_weight}_${timestamp}.txt"
    done

  done

done