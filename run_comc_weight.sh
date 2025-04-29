#!/bin/bash

dataset_folder="./testdatasets_json"
scenario="n021w4"
output_dir="./Output0429"

logs="logs-0429"


mkdir -p "${logs}/${scenario}"


for comc_weight in $(seq 50 50 1000)
do
  
  echo ">ComC weight: ${comc_weight}"
  python3 Init_nurse_pairs.py "$dataset_folder/$scenario/Sc-$scenario.json" "${output_dir}/${scenario}"
  
  for i in {1..12}

  do
    timestamp=$(date +"%Y%m%d_%H%M%S")
    sol_dir="${output_dir}/${scenario}/Solutions-ComC${comc_weight}-${i}"
    
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